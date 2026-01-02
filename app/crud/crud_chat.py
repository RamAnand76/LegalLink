from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.chat import ChatSession, ChatMessage


class CRUDChatSession:
    def create(self, db: Session, *, user_id: int, title: str = "New Chat") -> ChatSession:
        db_obj = ChatSession(user_id=user_id, title=title)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, id: int) -> Optional[ChatSession]:
        return db.query(ChatSession).filter(ChatSession.id == id).first()

    def get_by_user(self, db: Session, *, user_id: int, skip: int = 0, limit: int = 50) -> List[ChatSession]:
        return (
            db.query(ChatSession)
            .filter(ChatSession.user_id == user_id)
            .order_by(ChatSession.updated_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update_title(self, db: Session, *, db_obj: ChatSession, title: str) -> ChatSession:
        db_obj.title = title
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: int) -> None:
        obj = db.query(ChatSession).filter(ChatSession.id == id).first()
        if obj:
            db.delete(obj)
            db.commit()


class CRUDChatMessage:
    def create(self, db: Session, *, session_id: int, role: str, content: str) -> ChatMessage:
        db_obj = ChatMessage(session_id=session_id, role=role, content=content)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_session(self, db: Session, *, session_id: int) -> List[ChatMessage]:
        return (
            db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
            .all()
        )


chat_session = CRUDChatSession()
chat_message = CRUDChatMessage()
