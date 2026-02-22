from typing import Callable

from .ask_for_clarification import AskForClarificationTool

_TOOLS: list = [
    AskForClarificationTool(),
]

def get_tools() -> list[dict]:
    """
    Returns list of tools in MCP-compatible format: {name, description, inputSchema, responseSchema}.
    Used by tool_converter to build engine-specific tool declarations.
    """
    return [
        {
            "name": t.name,
            "description": t.description,
            "inputSchema": t.get_schema(),
            "responseSchema": t.get_response_schema(),
        }
        for t in _TOOLS
    ]


def get_tool_executor() -> Callable[[str, dict], str]:
    """
    Returns a function (name, args) -> result that executes the matching Python tool.
    Raises KeyError if tool name is not registered.
    """

    def executor(name: str, args: dict) -> str:
        for t in _TOOLS:
            if t.name == name:
                return t.execute(args or {})
        raise KeyError(f"Unknown Python tool: {name}")

    return executor


def is_tool(name: str) -> bool:
    """Returns True if the given tool name is a registered Python tool."""
    return any(t.name == name for t in _TOOLS)
