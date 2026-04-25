from datetime import datetime
from typing import Dict, List, Optional
from app.models.chat_models import Message


class ConversationService:
    """In-memory conversation flow and session management."""
    
    def __init__(self):
        self.sessions: Dict[str, Dict] = {}
        self.last_responses: Dict[str, str] = {}
    
    def create_session(self, session_id: str, greeting: str) -> Dict:
        self.sessions[session_id] = {
            "session_id": session_id,
            "messages": [
                Message(role="assistant", content=greeting, timestamp=datetime.utcnow().isoformat())
            ],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        self.last_responses[session_id] = greeting
        return self.sessions[session_id]
    
    def add_message(self, session_id: str, role: str, content: str) -> None:
        if session_id not in self.sessions:
            from app.services.ai_service import ai_service
            self.create_session(session_id, ai_service.get_greeting())
        
        message = Message(
            role=role,
            content=content,
            timestamp=datetime.utcnow().isoformat()
        )
        self.sessions[session_id]["messages"].append(message)
        self.sessions[session_id]["updated_at"] = datetime.utcnow().isoformat()
        
        if role == "assistant":
            self.last_responses[session_id] = content
    
    def get_history(self, session_id: str) -> List[Message]:
        if session_id in self.sessions:
            return self.sessions[session_id]["messages"]
        return []
    
    def get_last_response(self, session_id: str) -> Optional[str]:
        return self.last_responses.get(session_id)
    
    def clear_session(self, session_id: str) -> None:
        if session_id in self.sessions:
            del self.sessions[session_id]
        if session_id in self.last_responses:
            del self.last_responses[session_id]


conversation_service = ConversationService()