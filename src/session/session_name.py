
import os
import json
from files.config import LOG_DIR

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