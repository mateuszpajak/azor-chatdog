import uuid
from typing import List, Any, Union
import os
from files import session_files
from files.wal import append_to_wal
from llm.gemini_client import GeminiLLMClient
from llm.llama_client import LlamaClient
from llm.ollama_client import OllamaClient
from tools import resolve_tools_for_engine
from assistant import Assistant
from cli import console
from session.session_name import generate_session_name
from agents import get_agent_instance_by_name, get_default_agent_instance

# Context token limit

# Engine to Client Class mapping
ENGINE_MAPPING = {
    'LLAMA_CPP': LlamaClient,
    'GEMINI': GeminiLLMClient,
    'OLLAMA': OllamaClient,
}

THINKING_BUDGET = os.getenv("THINKING_BUDGET", 0)

class ChatSession:
    """
    Manages everything related to a single chat session.
    Encapsulates session ID, conversation history, assistant, and LLM chat session.
    """
    
    def __init__(self, assistant: Assistant, session_id: str | None = None, history: List[Any] | None = None):
        """
        Initialize a chat session.
        
        Args:
            assistant: Assistant instance that defines the behavior and model for this session
            session_id: Unique session identifier. If None, generates a new UUID.
            history: Initial conversation history. If None, starts empty.
        """
        self.assistant = assistant
        self.session_id = session_id or str(uuid.uuid4())
        self._history = history or []
        self._llm_client: Union[GeminiLLMClient, LlamaClient, OllamaClient, None] = None
        self._llm_chat_session = None
        self._max_context_tokens = 32768
        self._initialize_llm_session()

    def _initialize_llm_session(self):
        engine = os.getenv('ENGINE', 'GEMINI').upper()
        if engine not in ENGINE_MAPPING:
            valid_engines = ', '.join(ENGINE_MAPPING.keys())
            raise ValueError(f"ENGINE musi być jedną z wartości: {valid_engines}, otrzymano: {engine}")
        
        if self._llm_client is None:
            SelectedClientClass = ENGINE_MAPPING.get(engine, GeminiLLMClient)
            console.print_info(SelectedClientClass.preparing_for_use_message())
            self._llm_client = SelectedClientClass.from_environment()
            console.print_info(self._llm_client.ready_for_use_message())
        
        tools, tool_executor = resolve_tools_for_engine(engine)

        self._llm_chat_session = self._llm_client.create_chat_session(
            system_instruction=self.assistant.system_prompt,
            history=self._history,
            thinking_budget=THINKING_BUDGET,
            tools=tools,
            tool_executor=tool_executor,
        )

    @classmethod
    def load_from_file(cls, session_id: str) -> tuple['ChatSession | None', str | None]:
        """
        Loads a session from disk. Agent is read from the log file; if missing or unknown, AZOR is used.

        Args:
            session_id: ID of the session to load

        Returns:
            tuple: (ChatSession object or None, error_message or None)
        """
        history, agent_name, error = session_files.load_session_history(session_id)

        if error:
            return None, error

        assistant = get_agent_instance_by_name(agent_name) if agent_name else get_default_agent_instance()

        session = cls(assistant=assistant, session_id=session_id, history=history)
        return session, None

    def switch_agent(self, assistant: Assistant | None) -> bool:
        """
        Switches the current session to another agent by name. History is preserved; only system prompt changes.

        Returns:
            bool: True if switch succeeded, False if agent name is unknown.
        """
        if assistant is None:
            return False
        self.assistant = assistant
        self._initialize_llm_session()
        return True

    def save_to_file(self, session_name: str | None = None) -> tuple[bool, str | None]:
        """
        Saves this session to disk.
        Only saves if history has at least one complete exchange.
        
        Args:
            session_name: Optional session name to save (used for first query title generation)
        
        Returns:
            tuple: (success: bool, error_message: str | None)
        """
        # Sync history from LLM session before saving
        if self._llm_chat_session:
            self._history = self._llm_chat_session.get_history()
        
        return session_files.save_session_history(
            self.session_id,
            self._history,
            self.assistant.system_prompt,
            self._llm_client.get_model_name(),
            self.assistant.name,
            session_name
        )
    
    def send_message(self, text: str):
        """
        Sends a message to the LLM and returns the response.
        Updates internal history automatically and logs to WAL.
        
        Args:
            text: User's message
            
        Returns:
            Response object from Google GenAI
        """
        if not self._llm_chat_session:
            raise RuntimeError("LLM session not initialized")
        
        response = self._llm_chat_session.send_message(text)
        
        # Sync history after message
        self._history = self._llm_chat_session.get_history()
        
        # Log to WAL
        total_tokens = self.count_tokens()
        success, error = append_to_wal(
            session_id=self.session_id,
            prompt=text,
            response_text=response.text,
            total_tokens=total_tokens,
            model_name=self._llm_client.get_model_name(),
            agent=self.assistant.name
        )
        
        if not success and error:
            # We don't want to fail the entire message sending because of WAL issues
            # Just log the error to stderr or similar - but for now we'll silently continue
            pass
        
        return response

    def generate_session_name(self, session_id: str, text: str) -> str:
        user_message_count = sum(1 for h in self._history if h.get('role') == 'user')
        is_first_query = user_message_count == 1
        if is_first_query:
            return generate_session_name(session_id, text, self._llm_client)

        return None
    
    def get_history(self) -> List[Any]:
        """Returns the current conversation history."""
        # Always sync from LLM session to ensure consistency
        if self._llm_chat_session:
            self._history = self._llm_chat_session.get_history()
        return self._history
    
    def clear_history(self):
        """Clears all conversation history and reinitializes the LLM session."""
        self._history = []
        self._initialize_llm_session()
        self.save_to_file()
    
    def pop_last_exchange(self) -> bool:
        """
        Removes the last user-assistant exchange from history.
        
        Returns:
            bool: True if successful, False if insufficient history
        """
        current_history = self.get_history()
        
        if len(current_history) < 2:
            return False
        
        # Remove last 2 entries (user + assistant)
        self._history = current_history[:-2]
        
        # Reinitialize LLM session with modified history
        self._initialize_llm_session()
        
        self.save_to_file()
        
        return True
    
    def count_tokens(self) -> int:
        """
        Counts total tokens in the conversation history.
        
        Returns:
            int: Total token count
        """
        if not self._llm_client:
            return 0
        return self._llm_client.count_history_tokens(self._history)
    
    def is_empty(self) -> bool:
        """
        Checks if session has any complete exchanges.
        
        Returns:
            bool: True if history has less than 2 entries
        """
        return len(self._history) < 2
    
    def get_remaining_tokens(self) -> int:
        """
        Calculates remaining tokens based on context limit.
        
        Returns:
            int: Remaining token count
        """
        total = self.count_tokens()
        return self._max_context_tokens - total
    
    def get_token_info(self) -> tuple[int, int, int]:
        """
        Gets comprehensive token information for this session.
        
        Returns:
            tuple: (total_tokens, remaining_tokens, max_tokens)
        """
        total_tokens = self.count_tokens()
        remaining_tokens = self._max_context_tokens - total_tokens
        max_tokens = self._max_context_tokens
        return total_tokens, remaining_tokens, max_tokens
    
    @property
    def assistant_name(self) -> str:
        """
        Gets the display name of the assistant.
        
        Returns:
            str: The assistant's display name
        """
        return self.assistant.name