from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


# Chat Message Schemas
class ChatMessageBase(BaseModel):
    content: str


class ChatMessageCreate(ChatMessageBase):
    """Schema for sending a new message."""
    pass


class ChatMessage(BaseModel):
    """Schema for returning a message."""
    id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatMessageWithContext(ChatMessage):
    """Schema for returning a message with RAG context."""
    context_chunks: Optional[List[str]] = None


# Chat Session Schemas
class ChatSessionBase(BaseModel):
    title: Optional[str] = "New Chat"


class ChatSessionCreate(ChatSessionBase):
    """Schema for creating a new session."""
    pass


class ChatSessionUpdate(BaseModel):
    """Schema for updating a session (e.g., renaming)."""
    title: str


class ChatSession(BaseModel):
    """Schema for returning a session."""
    id: str  # UUID string
    title: str
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
    message: str = Field(..., min_length=1, max_length=10000, description="The user's message")
    session_id: Optional[str] = Field(None, description="Existing session UUID. If not provided, creates a new session.")
    document_id: Optional[str] = Field(None, description="ID of the uploaded document to use for context.")


class ChatResponse(BaseModel):
    """Schema for AI response with RAG context."""
    session_id: str
    user_message: ChatMessage
    assistant_message: ChatMessage
    context_chunks: List[str] = Field(default=[], description="RAG context chunks used for generating the response")


class SessionListItem(BaseModel):
    """Schema for session list items."""
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: Optional[int] = 0

    class Config:
        from_attributes = True
