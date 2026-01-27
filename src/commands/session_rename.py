from cli import console
from session.session_name import update_session_name

def rename_session_command(session_id: str, new_name: str):
    if not new_name or not new_name.strip():
        console.print_error("Błąd: Musisz podać nazwę sesji. Użycie: /session rename <nazwa>")
        return
    
    success, error = update_session_name(session_id, new_name.strip())
    
    if success:
        console.print_info(f"Pomyślnie zmieniono nazwę sesji na: '{new_name.strip()}'")
    else:
        console.print_error(f"Błąd podczas zmiany nazwy sesji: {error}")
