MCP_RESPONSE_SCHEMAS = {
    "listChatSessions": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "sessionId": {"type": "string", "description": "UUID sesji"},
                "sessionName": {"type": "string", "description": "Nazwa sesji czatu"},
                "lastModified": {
                    "type": "string",
                    "description": "Data ostatniej modyfikacji w formacie ISO 8601 (np. 2026-02-21T18:42:15.224658823Z).",
                },
            },
        },
    },
    "getChatSessions": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "sessionId": {"type": "string", "description": "UUID sesji"},
                "model": {"type": "string", "description": "Nazwa modelu LLM użytego w sesji"},
                "systemRole": {"type": "string", "description": "Prompt systemowy sesji"},
                "agent": {"type": "string", "description": "Nazwa agenta (np. AZOR)"},
                "sessionName": {"type": "string", "description": "Nazwa sesji czatu"},
                "fileName": {"type": "string", "description": "Nazwa pliku sesji na dysku"},
                "history": {
                    "type": "array",
                    "description": "Historia rozmowy",
                    "items": {
                        "type": "object",
                        "properties": {
                            "role": {"type": "string", "description": "Rola: user lub model"},
                            "timestamp": {"type": "string", "description": "Znacznik czasu wiadomości w formacie ISO 8601"},
                            "text": {"type": "string", "description": "Treść wiadomości"},
                        },
                    },
                },
            },
        },
    },
    "deleteChatSession": {
        "type": "object",
        "properties": {
            "deleted": {"type": "boolean", "description": "Czy plik sesji został pomyślnie usunięty"},
        },
    },
}
