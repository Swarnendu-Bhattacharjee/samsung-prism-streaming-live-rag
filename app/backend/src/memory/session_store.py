"""
Session-scoped memory store.
Per the spec: session-scoped memory only — no cross-session user profile.
"""

import uuid
from typing import List, Optional, Dict


class SessionStore:
    """In-memory session store. Swap for Redis in production."""

    def __init__(self):
        self.sessions: Dict[str, List[dict]] = {}
        self.documents: Dict[str, Dict[str, str]] = {}  # session_id -> {doc_id: text}

    def get_or_create(self, session_id: Optional[str]) -> str:
        """Get existing session or create a new one."""
        sid = session_id or str(uuid.uuid4())[:8]
        if sid not in self.sessions:
            self.sessions[sid] = []
            self.documents[sid] = {}
        return sid

    def add_message(self, session_id: str, role: str, content: str):
        """Add a message to the session history."""
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        self.sessions[session_id].append({"role": role, "content": content})

    def get_messages(self, session_id: str, max_turns: int = 20) -> List[dict]:
        """Get conversation history for a session."""
        if session_id not in self.sessions:
            return []
        turns = self.sessions[session_id][-max_turns * 2:]  # last N turns
        return turns

    def clear(self, session_id: str):
        """Clear a session's history."""
        self.sessions.pop(session_id, None)
        self.documents.pop(session_id, None)

    def add_document(self, session_id: str, doc_id: str, text: str):
        """Add a document to a session's corpus."""
        if session_id not in self.documents:
            self.documents[session_id] = {}
        self.documents[session_id][doc_id] = text

    def get_documents(self, session_id: str) -> Dict[str, str]:
        """Get all documents for a session."""
        return self.documents.get(session_id, {})

    def list_sessions(self) -> List[str]:
        """List all active session IDs."""
        return list(self.sessions.keys())
