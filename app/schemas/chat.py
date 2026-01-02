from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime


# Chat Message Schemas
class ChatMessageBase(BaseModel):
    content: str


class ChatMessageCreate(ChatMessageBase):
    """Schema for sending a new message."""
    pass


class ChatMessage(ChatMessageBase):
    """Schema for returning a message."""
    id: int
    session_id: int
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


# Chat Session Schemas
class ChatSessionBase(BaseModel):
    title: Optional[str] = "New Chat"


class ChatSessionCreate(ChatSessionBase):
    """Schema for creating a new session."""
    pass


class ChatSessionUpdate(BaseModel):
    """Schema for updating a session (e.g., renaming)."""
    title: str


class ChatSession(ChatSessionBase):
    """Schema for returning a session."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatSessionWithMessages(ChatSession):
    """Schema for returning a session with all messages."""
    messages: List[ChatMessage] = []


# Chat Request/Response
class ChatRequest(BaseModel):
    """Schema for sending a chat message."""
    message: str
    session_id: Optional[int] = None  # If None, creates a new session


class ChatResponse(BaseModel):
    """Schema for AI response."""
    session_id: int
    user_message: ChatMessage
    assistant_message: ChatMessage
