import json
import os
from typing import Any, Dict, List, Union

from assistant import Assistant, create_azor_assistant
from subagent import Subagent, create_snoppy_subagent
from files.config import CONFIG_DIR

CUSTOM_AGENTS_PATH = os.path.join(CONFIG_DIR, "custom_agents.json")

def get_default_agent_instance() -> Assistant:
    return create_azor_assistant()

def get_agent_instance_by_name(name: str) -> Union[Assistant, Subagent, None]:
    """
    Returns the agent instance (Assistant or Subagent) for the given name, or None if not found.
    Name comparison is case-insensitive.
    """
    if not name or not name.strip():
        return None
    key = name.strip().lower()
    for agent in get_all_agents():
        if agent["name"].strip().lower() == key:
            return agent["instance"]
    return None

def get_all_agents() -> List[Dict[str, Any]]:
    """
    Retrieves all available agents (assistants and subagents).

    Includes built-in assistants/subagents and custom subagents from custom_agents.json.
    Order: assistants, then built-in subagents, then custom subagents.

    Returns:
        List of dictionaries containing agent information:
        [
            {"type": "assistant"|"subagent", "name": str, "instance": Assistant|Subagent},
            ...
        ]
    """
    result: List[Dict[str, Any]] = []
    result.extend(get_default_agents())
    result.extend(get_custom_agents())

    return result

def get_default_agents() -> List[Dict[str, Any]]:
    result: List[Dict[str, Any]] = []

    # Assistants
    azor = create_azor_assistant()
    result.append({"type": "assistant", "name": azor.name, "instance": azor})

    # Built-in subagents
    snoppy = create_snoppy_subagent()
    result.append({"type": "subagent", "name": snoppy.name, "instance": snoppy})

    return result

def get_custom_agents() -> List[Dict[str, str]]:
    """
    Load custom agents from custom_agents.json.

    Returns:
        List of {"agent_name": str, "system_prompt": str}. Empty list if file missing or invalid.
    """
    if not os.path.exists(CUSTOM_AGENTS_PATH):
        return []
    try:
        with open(CUSTOM_AGENTS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        raw = data.get("agents", [])
        if not isinstance(raw, list):
            return []

        result = []
        for item in raw:
            if isinstance(item, dict) and "agent_name" in item and "system_prompt" in item:
                sub = Subagent(agent_name=item["agent_name"], system_prompt=item["system_prompt"])
                result.append({"type": "subagent", "name": sub.name, "instance": sub})

        return result
    except (json.JSONDecodeError, OSError):
        return []

def add_custom_agent(agent_name: str, system_prompt: str) -> tuple[Subagent | None, str | None]:
    if not agent_name.strip():
        return None, "Nazwa agenta nie może być pusta."
    if not system_prompt.strip():
        return None, "System prompt nie może być pusty."

    default_agents = get_default_agents()
    custom_agents = get_custom_agents()

    existing = {agent["name"] for agent in default_agents} | {agent["name"] for agent in custom_agents}
    if agent_name in existing:
        return None, f"Agent o nazwie {agent_name} już istnieje."

    custom_agents.append({"agent_name": agent_name, "system_prompt": system_prompt})
    ok, err = save_custom_agents(custom_agents)
    
    if not ok:
        return None, err or "Błąd zapisu."
    return Subagent(agent_name=agent_name, system_prompt=system_prompt), None

def save_custom_agents(agents: List[Dict[str, str]]) -> tuple[bool, str | None]:
    """
    Save custom agents to custom_agents.json.

    Returns:
        (True, None) on success, (False, error_message) on failure.
    """
    payload = {"agents": agents}
    try:
        with open(CUSTOM_AGENTS_PATH, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        return True, None
    except OSError as e:
        return False, str(e)