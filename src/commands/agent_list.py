from agents import get_all_agents
from cli import console

def list_agents_command():
    """Displays a formatted list of available agents."""
    agents = get_all_agents()
    if not agents:
        console.print_info("\nBrak dostępnych agentów.")
        return
        
    console.print_info("\n--- Dostępni agenci ---")
    for agent in agents:
        agent_type = agent["type"].upper()
        agent_name = agent["name"]
        console.print_info(f"- {agent_type}: {agent_name}")
    console.print_info("----------------------")
