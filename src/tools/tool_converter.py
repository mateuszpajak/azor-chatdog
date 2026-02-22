from google.genai import types
from mcp_client import MCP_RESPONSE_SCHEMAS


def to_gemini_tools(tools: list[dict]) -> list[types.Tool]:
    declarations = []
    for tool in tools:
        schema = tool.get("inputSchema", {})
        name = tool["name"]
        response_schema = tool.get("responseSchema") or MCP_RESPONSE_SCHEMAS.get(name)
        declarations.append(
            types.FunctionDeclaration(
                name=name,
                description=tool.get("description", ""),
                parameters_json_schema=schema if schema.get("properties") else None,
                response_json_schema=response_schema,
            )
        )
    names = [t["name"] for t in tools]
    print("Dostępne tools:", names)

    return [types.Tool(function_declarations=declarations)]
