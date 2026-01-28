from agents import add_custom_agent
from cli import console


def add_agent_command(parts: list[str]) -> None:
    """
    Handles /agent new <agent_name> <system_prompt>.
    Parses args, calls add_custom_agent, prints success or error.
    """
    if len(parts) < 4:
        console.print_error("Błąd: Użycie: /agent new <agent_name> <system_prompt>")
        return

    agent_name = parts[2]
    system_prompt = " ".join(parts[3:]).strip()
        
    subagent, err = add_custom_agent(agent_name, system_prompt)
    if err:
        console.print_error(f"Błąd: {err}")
        return
        
    console.print_info(f"\nDodano custom subagenta: {subagent.name}")
