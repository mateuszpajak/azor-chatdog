import os

from cli import console
from datetime import datetime
from files.config import OUTPUT_DIR
from TTS.api import TTS
from pydub import AudioSegment
from typing import List, Any

AGENT_VOICE_SAMPLE = os.environ.get('AGENT_VOICE_SAMPLE_PATH')
USER_VOICE_SAMPLE = os.environ.get('USER_VOICE_SAMPLE_PATH')
AUDIO_MODULE_NAME = os.environ.get('AUDIO_MODULE_NAME')

tts_instance = None

def load_model():
    if not AGENT_VOICE_SAMPLE:
        console.print_error("❌ Brak ścieżki do pliku próbki głosu asystenta.")
        return
    if not USER_VOICE_SAMPLE:
        console.print_error("❌ Brak ścieżki do pliku próbki głosu użytkownika.")
        return
    if not AUDIO_MODULE_NAME:
        console.print_error("❌ Brak nazwy modułu TTS.")
        return

    global tts_instance
    try:
        console.print_info("\n🤖 Ładowanie modelu TTS...")
        tts_instance = TTS(AUDIO_MODULE_NAME).to("cpu")
        console.print_info("✅ Model załadowany pomyślnie.")
    except Exception as e:
        console.print_error(f"❌ Błąd ładowania modelu: {e}")

def generate_last_model_message(history: List[Any], voice_sample: str = AGENT_VOICE_SAMPLE):
    text = [m['parts'][0]['text'] for m in history if m['role'] == 'model'][-1]

    datetime_string = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file_name = f"azor_voice_{datetime_string}.wav"
    output_path = os.path.join(OUTPUT_DIR, output_file_name)

    generate_audio(text, voice_sample, output_file_name, output_path)

def generate_audio(text: str, voice_sample: str, output_file_name: str, output_path: str, verbose: bool = True):
    if not voice_sample:
        console.print_error("❌ Brak ścieżki do pliku próbki głosu.")
        return False
    if not tts_instance:
        console.print_error("❌ Brak załadowanego modelu TTS.")
        return False

    if verbose:
        console.print_info(f"🤖 Rozpoczynam generowanie głosu Azora do pliku: {output_file_name}.") 

    tts_instance.tts_to_file(
        text=text,
        speaker_wav=voice_sample,
        language='pl',
        file_path=output_path
    )

    if verbose:
        console.print_info(f"✅ Sukces! Nagranie zapisano w: {output_file_name}")

    return True

def generate_chat(history: List[Any]):
    dialogue = [part['text'] for entry in history for part in entry.get('parts', [])]

    chunks_dir = os.path.join(OUTPUT_DIR, "chunks")
    os.makedirs(chunks_dir, exist_ok=True)

    chunks = []
    datetime_string = datetime.now().strftime("%Y%m%d_%H%M%S")

    for i, text in enumerate(dialogue):
        voice_sample = USER_VOICE_SAMPLE if i % 2 == 0 else AGENT_VOICE_SAMPLE

        output_filename = f"user_voice_{datetime_string}.wav" if i % 2 == 0 else f"azor_voice_{datetime_string}.wav"
        output_path = os.path.join(chunks_dir, output_filename)
        
        is_generated = generate_audio(text, voice_sample, output_filename, output_path, False)
        if is_generated:
            chunks.append(output_path)

    output_filename = f"chat_{datetime_string}.wav"
    output_path = os.path.join(OUTPUT_DIR, output_filename)


    console.print_info(f"🤖 Rozpoczynam zapis konwersacji do pliku: {output_filename}.") 
    is_merged = merge_wav_files(chunks, output_path)
    if is_merged:
        console.print_info(f"✅ Sukces! Nagranie zapisano w: {output_filename}")
    else:
        console.print_error(f"❌ Błąd zapisu konwersacji do pliku: {output_filename}"
)

def merge_wav_files(file_paths, output_path):
    if not file_paths:
        raise ValueError("Lista plików nie może być pusta.")

    try:
        combined = AudioSegment.empty()
        for path in file_paths:
            current_segment = AudioSegment.from_wav(path)
            combined += current_segment

        combined.export(output_path, format="wav")
        return True
    except Exception as e:
        return False