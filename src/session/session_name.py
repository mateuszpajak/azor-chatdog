
import os
import json
from files.config import LOG_DIR
from cli import console

def update_session_name(session_id: str, new_name: str) -> tuple[bool, str | None]:
    log_path = os.path.join(LOG_DIR, f"{session_id}-log.json")
    if not os.path.exists(log_path):
        return False, f"Session file for ID '{session_id}' not found."
    
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            log_data = json.load(f)
        
        log_data['session_name'] = new_name
        
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=4, ensure_ascii=False)
        
        return True, None
    except Exception as e:
        return False, f"Error updating session name: {e}"

def read_session_name(session_id: str) -> str:
    log_path = os.path.join(LOG_DIR, f"{session_id}-log.json")
    if not os.path.exists(log_path):
        return ""

    try:
        with open(log_path, "r", encoding="utf-8") as f:
            log_data = json.load(f)
            return (log_data.get("session_name") or "").strip()
    except Exception:
        return ""

def generate_session_name(user_prompt: str, llm_client) -> str:
    title_system_prompt = """
        Stwórz krótki, zwięzły tytuł (maksymalnie 50-60 znaków) podsumowujący następujące zapytanie użytkownika. 
        Tytuł powinien być w języku polskim i opisywać główny temat zapytania. Zwróć TYLKO tytuł, bez dodatkowych komentarzy.
    """
    title_prompt = f"Zapytanie użytkownika: {user_prompt}\n\nTytuł:"
    
    try:
        temp_session = llm_client.create_chat_session(
            system_instruction=title_system_prompt,
            history=[],
            thinking_budget=0
        )
        
        response = temp_session.send_message(title_prompt)
        title = response.text.strip()
        if len(title) > 60:
            title = title[:57] + "..."
        
        return title
    except Exception as e:
        console.print_error(f"Błąd podczas generowania tytułu sesji: {e}")
        return user_prompt[:20] + "..."