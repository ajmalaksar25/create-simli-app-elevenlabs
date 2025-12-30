import uuid
from typing import Dict, Optional
from models import ScreeningContext


class SessionManager:
    """Manages screening sessions in memory"""
    
    def __init__(self):
        self.sessions: Dict[str, ScreeningContext] = {}
    
    def create_session(self, context: ScreeningContext) -> str:
        """Create a new session and return session ID"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = context
        return session_id
    
    def get_session(self, session_id: str) -> Optional[ScreeningContext]:
        """Get session context by ID"""
        return self.sessions.get(session_id)
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def session_exists(self, session_id: str) -> bool:
        """Check if session exists"""
        return session_id in self.sessions


# Global session manager instance
session_manager = SessionManager()

