from abc import ABC, abstractmethod


class BaseTool(ABC):
    """
    Base class for all Python tools.
    Subclasses must implement name, description, get_schema, and execute.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Tool identifier (e.g. 'askForClarification')."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Description for the model to understand when to use this tool."""
        pass

    @abstractmethod
    def get_schema(self) -> dict:
        """
        JSON Schema compatible with inputSchema (properties, required).
        Used by tool_converter to build FunctionDeclaration.
        """
        pass

    @abstractmethod
    def get_response_schema(self) -> dict:
        """
        JSON Schema for tool response structure.
        Used by tool_converter to build FunctionDeclaration.
        """
        pass

    @abstractmethod
    def execute(self, args: dict) -> str:
        """
        Execute the tool with given arguments.
        Returns result as string for the model.
        """
        pass
