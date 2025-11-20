# Session Service
import structlog
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

logger = structlog.get_logger()

class SessionService:
    """Service to manage user sessions"""
    
    def __init__(self):
        logger.info("SessionService initialized")
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.session_timeout = timedelta(hours=24)
    
    def create_session(self, user_id: str) -> str:
        """Create a new session for user"""
        session_id = f"session_{user_id}_{datetime.now().timestamp()}"
        
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "created_at": datetime.now(),
            "last_activity": datetime.now(),
            "message_count": 0,
            "context": {},
            "history": []
        }
        
        self.sessions[session_id] = session_data
        logger.info("Session created", session_id=session_id, user_id=user_id)
        self.sessions[session_id] = session_data
        logger.info("Session created", session_id=session_id, user_id=user_id)
        return session_id
    
    def get_active_session(self, user_id: str) -> str:
        """Get active session for user or create new one"""
        # Check for existing active session
        for session_id, session in self.sessions.items():
            if session["user_id"] == user_id:
                # Check if expired
                if datetime.now() - session["last_activity"] <= self.session_timeout:
                    # Update activity time
                    session["last_activity"] = datetime.now()
                    logger.info("Active session found", session_id=session_id, user_id=user_id)
                    return session_id
        
        # No active session found, create new one
        return self.create_session(user_id)
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            
            # Check if session is expired
            if datetime.now() - session["last_activity"] > self.session_timeout:
                logger.info("Session expired", session_id=session_id)
                self.sessions.pop(session_id, None)
                return None
            
            # Update last activity
            session["last_activity"] = datetime.now()
            return session
        
        return None
    
    def update_session_context(self, session_id: str, key: str, value: Any) -> bool:
        """Update session context"""
        session = self.get_session(session_id)
        if session:
            session["context"][key] = value
            logger.info("Session context updated", session_id=session_id, key=key)
            return True
        return False
    
    def increment_message_count(self, session_id: str) -> bool:
        """Increment message count for session"""
        session = self.get_session(session_id)
        if session:
            session["message_count"] += 1
            return True
        return False

    def add_message(self, session_id: str, role: str, content: str) -> bool:
        """Add a message to the session history"""
        session = self.get_session(session_id)
        if session:
            message = {
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat()
            }
            if "history" not in session:
                session["history"] = []
            session["history"].append(message)
            # Keep history limited to last 50 messages to prevent bloating
            if len(session["history"]) > 50:
                session["history"] = session["history"][-50:]
            return True
        return False

    def get_chat_history(self, session_id: str, limit: int = 10) -> list:
        """Get recent chat history"""
        session = self.get_session(session_id)
        if session and "history" in session:
            return session["history"][-limit:]
        return []
    
    def cleanup_expired_sessions(self) -> int:
        """Remove expired sessions and return count of removed sessions"""
        current_time = datetime.now()
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            if current_time - session["last_activity"] > self.session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            self.sessions.pop(session_id, None)
        
        logger.info("Expired sessions cleaned up", count=len(expired_sessions))
        return len(expired_sessions)