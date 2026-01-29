# Azor the chatdog - documentation

## 🚀 Project Overview

Azor the chatdog is a command-line interface chat application that provides an interactive, persistent chat experience with configurable language models. It supports both cloud-based models (Google Gemini) and local LLaMA models, offering a unified interface for interacting with AI assistants.

## 🛠️ Setup Instructions

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```

2. Activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure your environment:
   - Create a `.env` file with your API keys and model settings
   - For Gemini: add `GEMINI_API_KEY` and `MODEL_NAME`
   - For LLaMA: add `LLAMA_MODEL_PATH` and model-specific parameters

## 📂 Architecture Overview

**System Diagram**:
```
+-------------------+
|    User Interface |
| (prompt-toolkit)  |
+-------------------+
          |
          v
+-------------------+
|     Command       |
|    Handler        |
+-------------------+
          |
          v
+-------------------+
|     Session Manager |
| (session_manager.py)|
+-------------------+
          |
          v
+-------------------+
|    Chat Session   |
| (chat_session.py) |
+-------------------+
          |
          v
+-------------------+
|    LLM Client     |
| (gemini_client.py  |
|  or llama_client.py)|
+-------------------+
          |
          v
+-------------------+
|  Model (API/GGUF)|
+-------------------+
```

**Core Components**:
- **Session Manager**: Orchestrates session lifecycle and state
- **Chat Session**: Manages individual conversation history and state
- **LLM Client**: Unified interface for different model types
- **Persistence**: WAL logging and session file storage
- **Subagent**: Entity with `agent_name` and `system_prompt`; package `subagent` provides the `Subagent` class for specialized sub-agents

## 🚦 Command Reference

### Core Commands
```
/session list        # List all available sessions
/session display     # Show full session history
/session summary     # Show concise session summary
/session new         # Create a new session
/session clear       # Clear current session
/session pop         # Remove last message

/switch <ID>         # Switch to existing session
/help                # Show help information
/exit, /quit         # Exit the application
```

### Agent Commands
```
/agent list          # List available agents
/agent current       # Show currently set agent
/agent new ...       # Add custom subagent
/agent switch <NAME> # Switch session to given agent
```

### Usage Examples
- Start new session: `python src/run.py`
- Load specific session: `python src/run.py --session-id=abc123`
- Switch sessions: `/switch xyz789`
- Get help: `/help`

## 📚 Contribution Guidelines

1. **Documentation**: Always update `README.md` and `DOCS.md` when making changes
2. **Code Style**: Follow existing patterns and conventions
3. **Testing**: Ensure all changes pass linting and type checking
4. **Commit Messages**: Use clear, descriptive messages focusing on the "why" not just the "what"
5. **Command Architecture**: Follow the established patterns for new commands

## 📂 File Structure

```
src/
├── chat.py          # Main application logic
├── assistant/
│   ├── __init__.py
│   ├── assistent.py
│   └── azor.py
├── subagent/
│   ├── __init__.py
│   └── subagent.py
│   └── snoppy.py
├── cli/
│   ├── args.py
│   ├── console.py
│   └── prompt.py
├── llm/
│   ├── __init__.py
│   ├── gemini_client.py
│   ├── gemini_validation.py
│   ├── llama_client.py
│   └── llama_validation.py
├── command_handler.py
├── pdf.py
├── commands/
│   ├── __init__.py
│   ├── session_display.py
│   ├── session_list.py
│   ├── session_remove.py
│   ├── session_summary.py
│   ├── session_to_pdf.py
│   └── welcome.py
├── run.py
├── files/
│   ├── __init__.py
│   ├── config.py
│   └── session_files.py
└── session/
    ├── __init__.py
    ├── chat_session.py
    └── session_manager.py
```

## 🔍 Debugging Tips

- Check `~/.azor/azor-wal.json` for all transaction logs
- Examine `~/.azor/<session-id>-log.json` for session-specific data
- Use `ls ~/.azor/` to list all available sessions
- Check `.env` file for configuration issues
- Verify model paths and API keys are correctly set

## ❓ Need Help?

If you have questions about the codebase or how to contribute, please refer to the documentation or reach out to the maintainers.
