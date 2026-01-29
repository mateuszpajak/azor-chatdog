from session.chat_session import ChatSession
from subagent import Subagent
from cli import console

def show_current_agent_command(session: ChatSession) -> None:
    """
    Displays the currently set agent for the session.
    """
    name = session.assistant_name
    agent_type = "subagent" if isinstance(session.assistant, Subagent) else "assistant"
    console.print_info(f"Aktualny agent: {name} ({agent_type})")
