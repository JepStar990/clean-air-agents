from typing import Dict, Any
SESSIONS: Dict[str, Dict[str, Any]] = {}

def get_session(user_id: str) -> Dict[str, Any]:
    return SESSIONS.setdefault(user_id, {"history": [], "preferences": {}})

