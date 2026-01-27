from files import session_files
from cli import console

def list_sessions_command():
    """Displays a formatted list of available sessions."""
    sessions = session_files.list_sessions()
    if sessions:
        console.print_help("\n--- Dostępne zapisane sesje (ID) ---")
        for session in sessions:
            prefix = f"- ID: {session['id']}"
            if session.get('session_name'):
                prefix += f" TITLE: {session['session_name']}"

            if session.get('error'):
                console.print_error(f"{prefix} ({session['error']})")
            else:
                console.print_help(f"{prefix} (Wiadomości: {session['messages_count']}, Ost. aktywność: {session['last_activity']})")
        console.print_help("------------------------------------")
    else:
        console.print_help("\nBrak zapisanych sesji.")
