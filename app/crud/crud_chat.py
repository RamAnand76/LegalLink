import json
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.chat import ChatSession, ChatMessage


class CRUDChatSession:
    def create(self, db: Session, *, user_id: int, title: str = "New Chat") -> ChatSession:
        """Create a new chat session with auto-generated UUID."""
        db_obj = ChatSession(user_id=user_id, title=title)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, id: str) -> Optional[ChatSession]:
        """Get a chat session by UUID."""
        return db.query(ChatSession).filter(ChatSession.id == id).first()

    def get_by_user(self, db: Session, *, user_id: int, skip: int = 0, limit: int = 50) -> List[ChatSession]:
        """Get all chat sessions for a user, ordered by most recent."""
        return (
            db.query(ChatSession)
            .filter(ChatSession.user_id == user_id)
            .order_by(ChatSession.updated_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update_title(self, db: Session, *, db_obj: ChatSession, title: str) -> ChatSession:
        """Update the title of a chat session."""
        db_obj.title = title
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: str) -> bool:
        """Delete a chat session by UUID."""
        obj = db.query(ChatSession).filter(ChatSession.id == id).first()
        if obj:
            db.delete(obj)
            db.commit()
            return True
        return False

    def get_message_count(self, db: Session, *, session_id: str) -> int:
        """Get the number of messages in a session."""
        return db.query(ChatMessage).filter(ChatMessage.session_id == session_id).count()


class CRUDChatMessage:
    def create(
        self, 
        db: Session, 
        *, 
        session_id: str, 
        role: str, 
        content: str,
        context_chunks: Optional[List[str]] = None
    ) -> ChatMessage:
        """Create a new chat message."""
        context_json = json.dumps(context_chunks) if context_chunks else None
        db_obj = ChatMessage(
            session_id=session_id, 
            role=role, 
            content=content,
            context_chunks=context_json
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_session(self, db: Session, *, session_id: str) -> List[ChatMessage]:
        """Get all messages for a session, ordered by creation time."""
        return (
            db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
            .all()
        )

    def get_context_chunks(self, message: ChatMessage) -> List[str]:
        """Parse and return context chunks from a message."""
        if message.context_chunks:
            try:
                return json.loads(message.context_chunks)
            except json.JSONDecodeError:
                return []
        return []


chat_session = CRUDChatSession()
chat_message = CRUDChatMessage()
