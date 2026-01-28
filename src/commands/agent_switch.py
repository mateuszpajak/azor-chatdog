from session.chat_session import ChatSession
from agents import get_agent_instance_by_name
from cli import console

def switch_agent_command(session: ChatSession, agent_name: str) -> None:
    """
    Switches the current session to the specified agent.
    """
    assistant = get_agent_instance_by_name(agent_name)
    if not assistant:
        console.print_error(f"Błąd: Nieznany agent: {agent_name}. Użyj /agent list.")
        return
    
    if session.switch_agent(assistant):
        console.print_info(f"Przełączono na agenta: {session.assistant_name}")
    else:
        console.print_error(f"Błąd: Nieznany agent: {agent_name}. Użyj /agent list.")