"""
Agents module initialization
Exports functions for discovering and retrieving available agents.
"""
from .agents import add_custom_agent, get_all_agents, get_agent_instance_by_name, get_default_agent_instance

__all__ = ['add_custom_agent', 'get_all_agents', 'get_agent_instance_by_name', 'get_default_agent_instance']
