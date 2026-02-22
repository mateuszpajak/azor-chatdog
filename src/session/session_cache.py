"""
In-memory cache for session metadata used by the prompt autocomplete.
"""
from files import session_files

_sessions: dict[str, str] = {}

def init_session_cache() -> None:
    global _sessions
    sessions_data = session_files.list_sessions()
    _sessions = {
        s['id']: s.get('session_name', '')
        for s in sessions_data
        if s.get('error') is None
    }

def set_sessions(sessions: dict[str, str]) -> None:
    global _sessions
    _sessions = dict(sessions)


def upsert_session(session_id: str, name: str = "") -> None:
    _sessions[session_id] = name


def remove_session(session_id: str) -> None:
    _sessions.pop(session_id, None)


def get_sessions() -> dict[str, str]:
    return _sessions
