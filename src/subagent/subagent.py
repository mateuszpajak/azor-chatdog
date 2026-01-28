"""
Subagent class definition
Defines the Subagent class that encapsulates subagent configuration.
"""


class Subagent:
    """
    Represents a subagent with agent name and system prompt.
    Encapsulates the subagent's identity and behavior configuration.
    """

    def __init__(self, agent_name: str, system_prompt: str):
        """
        Initialize a Subagent with agent name and system prompt.

        Args:
            agent_name: The display name of the subagent
            system_prompt: The system instruction/prompt that defines the subagent's behavior
        """
        self._agent_name = agent_name
        self._system_prompt = system_prompt

    @property
    def name(self) -> str:
        """Get the display name for this subagent."""
        return self._agent_name

    @property
    def system_prompt(self) -> str:
        """Get the system prompt for this subagent."""
        return self._system_prompt
