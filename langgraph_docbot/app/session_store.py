"""
Simple session manager for storing dialog state between requests.
"""
import json
import os
from typing import Dict, Any, Optional
from datetime import datetime
from .config import settings


# In-memory store for sessions
_sessions: Dict[str, Dict[str, Any]] = {}


def get_session_file_path() -> str:
    """Returns path to session storage file."""
    return os.path.join(os.path.dirname(settings.MEMORY_FILE), "conversation_sessions.json")


def load_sessions() -> Dict[str, Dict[str, Any]]:
    """Loads sessions from file."""
    file_path = get_session_file_path()
    if not os.path.exists(file_path):
        return {}
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_sessions(sessions: Dict[str, Dict[str, Any]]):
    """Saves sessions to file."""
    file_path = get_session_file_path()
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(sessions, f, ensure_ascii=False, indent=2)


def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Gets session state."""
    # First check in-memory store
    if session_id in _sessions:
        return _sessions[session_id]
    
    # If not in memory, load from file
    sessions = load_sessions()
    if session_id in sessions:
        _sessions[session_id] = sessions[session_id]
        return sessions[session_id]
    
    return None


def save_session(session_id: str, state: Dict[str, Any]):
    """Saves session state."""
    state["last_updated"] = datetime.now().isoformat()
    _sessions[session_id] = state
    
    # Save to file
    sessions = load_sessions()
    sessions[session_id] = state
    save_sessions(sessions)


def create_session(session_id: str, initial_state: Dict[str, Any]) -> Dict[str, Any]:
    """Creates new session."""
    initial_state["created_at"] = datetime.now().isoformat()
    initial_state["last_updated"] = datetime.now().isoformat()
    _sessions[session_id] = initial_state
    
    # Save to file
    sessions = load_sessions()
    sessions[session_id] = initial_state
    save_sessions(sessions)
    
    return initial_state


def delete_session(session_id: str):
    """Deletes session."""
    if session_id in _sessions:
        del _sessions[session_id]
    
    sessions = load_sessions()
    if session_id in sessions:
        del sessions[session_id]
        save_sessions(sessions)

