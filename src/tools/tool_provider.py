from typing import Callable, Protocol

from mcp_client import McpClient

from .tool_registry import get_tools, get_tool_executor
from .tool_converter import to_gemini_tools

TOOL_CONVERTER_BY_ENGINE = {"GEMINI": to_gemini_tools}


class ToolProvider(Protocol):
    def list_tools(self) -> list[dict]:
        """Returns tools in MCP format: {name, description, inputSchema}."""
        ...

    def call_tool(self, name: str, arguments: dict) -> str:
        """Executes the tool and returns result as string."""
        ...


class ToolProvider:
    def list_tools(self) -> list[dict]:
        return get_tools()

    def call_tool(self, name: str, arguments: dict) -> str:
        return get_tool_executor()(name, arguments or {})


class McpToolProvider:
    def __init__(self, mcp_client):
        self._mcp = mcp_client

    def list_tools(self) -> list[dict]:
        if not self._mcp.enabled:
            return []
        try:
            return self._mcp.list_tools()
        except Exception as e:
            from cli import console
            console.print_error(f"Nie udało się pobrać narzędzi MCP: {e}")
            return []

    def call_tool(self, name: str, arguments: dict) -> str:
        return self._mcp.call_tool(name, arguments or {})


class CompositeToolProvider:
    def __init__(self, providers: list[ToolProvider]):
        self._providers = providers
        self._name_to_provider: dict[str, ToolProvider] = {}

    def list_tools(self) -> list[dict]:
        self._name_to_provider.clear()
        result = []
        for provider in self._providers:
            for tool in provider.list_tools():
                name = tool["name"]
                if name not in self._name_to_provider:
                    self._name_to_provider[name] = provider
                    result.append(tool)
        return result

    def call_tool(self, name: str, arguments: dict) -> str:
        provider = self._name_to_provider.get(name)
        if provider is None:
            raise KeyError(f"Nieznane narzędzie: {name}")
        return provider.call_tool(name, arguments or {})


def resolve_tools_for_engine(engine: str) -> tuple[list | None, Callable | None]:
    converter = TOOL_CONVERTER_BY_ENGINE.get(engine)
    if not converter:
        return None, None

    mcp_client = McpClient()
    provider = CompositeToolProvider([
        ToolProvider(),
        McpToolProvider(mcp_client),
    ])
    all_tools = provider.list_tools()

    return converter(all_tools), provider.call_tool
