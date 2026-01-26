import os
import requests
import tiktoken

from typing import Optional, List, Any, Dict
from openai import OpenAI
from dotenv import load_dotenv
from cli import console
from .ollama_validation import OllamaConfig

DEFAULT_TEMPERATURE = 1
DEFAULT_TOP_P = 1

class OllamaChatSession:    

    def __init__(self, client: OpenAI, model_name: str, system_instruction: str, temperature: float, top_p: float, history: Optional[List[Dict]] = None):
        self.client = client
        self.model_name = model_name
        self.system_instruction = system_instruction
        self.temperature = temperature
        self.top_p = top_p
        self._history = history or []
        
    def send_message(self, text: str) -> Any:
        messages = [{"role": "system", "content": self.system_instruction}]
        
        for msg in self._history:
            role = "assistant" if msg["role"] == "model" else "user"
            messages.append({"role": role, "content": msg["parts"][0]["text"]})
            
        messages.append({"role": "user", "content": text})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                top_p=self.top_p
            )
            
            response_text = response.choices[0].message.content
            
            self._history.append({"role": "user", "parts": [{"text": text}]})
            self._history.append({"role": "model", "parts": [{"text": response_text}]})
            
            return OllamaResponse(response_text)
            
        except Exception as e:
            console.print_error(f"Błąd Ollama API: {e}")
            error_text = "Błąd komunikacji z lokalnym serwerem modelu."
            return OllamaResponse(error_text)

    def get_history(self) -> List[Dict]:
        return self._history

class OllamaResponse:
    def __init__(self, text: str):
        self.text = text

class OllamaClient:    
    def __init__(self, model_name: str, base_url: str, temperature: float, top_p: float):
        self.model_name = model_name
        self.temperature = temperature
        self.top_p = top_p
        self._ollama_client = OpenAI(base_url=base_url, api_key="dummy")
    
    @staticmethod
    def preparing_for_use_message() -> str:
        return "🌐 Łączenie z lokalnym serwerem Ollama..."

    @classmethod
    def from_environment(cls) -> 'OllamaClient':
        load_dotenv()
        config = OllamaConfig(
            model_name=os.getenv('OLLAMA_MODEL_NAME', 'local-model'),
            base_url=os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434/v1'),
            temperature=os.getenv('TEMPERATURE', DEFAULT_TEMPERATURE),
            top_p=os.getenv("TOP_P", DEFAULT_TOP_P)
        )
        return cls(
            model_name=config.model_name,
            base_url=config.base_url,
            temperature=config.temperature,
            top_p=config.top_p
        )

    def create_chat_session(self, 
                           system_instruction: str, 
                           history: Optional[List[Dict]] = None,
                           thinking_budget: int = 0) -> OllamaChatSession:
        return OllamaChatSession(
            client=self._ollama_client,
            model_name=self.model_name,
            system_instruction=system_instruction,
            temperature=self.temperature,
            top_p=self.top_p,
            history=history or []
        )
    
    def count_history_tokens(self, history: List[Dict]) -> int:
        if not history:
            return 0
        
        try:
            try:
                encoding = tiktoken.encoding_for_model(self.model_name)
            except KeyError:
                encoding = tiktoken.get_encoding("cl100k_base")

            tokens_per_message = 3
            tokens_per_name = 1
            num_tokens = 0
            
            for message in history:
                num_tokens += tokens_per_message

                if "parts" in message and message["parts"]:
                    text_content = message["parts"][0].get("text", "")
                    if text_content:
                        num_tokens += len(encoding.encode(text_content))
                
                if "role" in message:
                    num_tokens += len(encoding.encode(message["role"]))
            
            # Każda odpowiedź jest poprzedzona <|start|>assistant<|message|>
            num_tokens += 3 
            return num_tokens

        except Exception as e:
            console.print_error(f"Błąd podczas liczenia tokenów: {e}")
            return 0

    def ready_for_use_message(self) -> str:
        return f"✅ Połączono z serwerem API (Model: {self.model_name}) " +  f"\n⚙️  Ustawione parametry: temperature: {self.temperature}, top_p: {self.top_p} ";
    
    def get_model_name(self) -> str:
        """Returns the currently configured model name."""
        return self.model_name
    
    @property
    def client(self):
        return self._ollama_client