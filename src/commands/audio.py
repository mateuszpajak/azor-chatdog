from audio.audio_generator import generate_last_model_message, generate_chat
from typing import List, Any
from cli import console

def generate_audio(history: List[Any]):
    if not history:
        console.print_error("❌ Brak historii sesji.")
        return
    
    generate_last_model_message(history)

def generate_audio_all(history: List[Any]):
    if not history:
        console.print_error("❌ Brak historii sesji.")
        return
    
    generate_chat(history)