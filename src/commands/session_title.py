from cli import console
from session.session_name import read_session_name

def show_session_title_command(session_id: str):
    name = read_session_name(session_id)
    if name:
        console.print_info(f"Tytuł bieżącej sesji: {name}")
    else:
        console.print_info("Brak tytułu dla bieżącej sesji.")
