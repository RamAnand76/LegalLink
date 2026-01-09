from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


# Chat Message Schemas
class ChatMessageBase(BaseModel):
    content: str = Field(..., example="What is Section 80 of the Code of Civil Procedure?")


class ChatMessageCreate(ChatMessageBase):
    """Schema for sending a new message."""
    pass


class ChatMessage(BaseModel):
    """Schema for returning a message."""
    id: int = Field(..., example=1)
    role: str = Field(..., example="user")
    content: str = Field(..., example="What is Section 80 of the Code of Civil Procedure?")
    created_at: datetime = Field(..., example="2026-01-04T10:30:00")

    model_config = ConfigDict(from_attributes=True)


class ChatMessageWithContext(ChatMessage):
    """Schema for returning a message with RAG context."""
    context_chunks: Optional[List[str]] = Field(
        None, 
        example=["Section 80. Notice. (1) Save as otherwise provided...", "No suit shall be instituted against the Government..."]
    )


# Chat Session Schemas
class ChatSessionBase(BaseModel):
    title: Optional[str] = Field("New Chat", example="Legal Query - Tenant Rights")


class ChatSessionCreate(ChatSessionBase):
    """Schema for creating a new session."""
    pass


class ChatSessionUpdate(BaseModel):
    """Schema for updating a session (e.g., renaming)."""
    title: str = Field(..., example="Property Dispute Discussion")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Property Dispute Discussion"
            }
        }
    )


class ChatSession(BaseModel):
    """Schema for returning a session."""
    id: str = Field(..., example="e1479787-7c18-4072-9d16-04ac7082fef9")
    title: str = Field(..., example="Legal Query - Tenant Rights")
    created_at: datetime = Field(..., example="2026-01-04T10:30:00")
    updated_at: datetime = Field(..., example="2026-01-04T10:35:00")

    model_config = ConfigDict(from_attributes=True)


class ChatSessionWithMessages(ChatSession):
    """Schema for returning a session with all messages."""
    messages: List[ChatMessage] = []


# Chat Request/Response
class ChatRequest(BaseModel):
    """Schema for sending a chat message."""
    message: str = Field(
        ..., 
        min_length=1, 
        max_length=10000, 
        description="The user's message",
        example="What is the procedure to evict a tenant who hasn't paid rent for 5 months?"
    )
    session_id: Optional[str] = Field(
        None, 
        description="Existing session UUID. If not provided, creates a new session.",
        example="e1479787-7c18-4072-9d16-04ac7082fef9"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "What is the procedure to evict a tenant who hasn't paid rent for 5 months?",
                "session_id": None
            }
        }
    )


class ChatResponse(BaseModel):
    """Schema for AI response with RAG context."""
    session_id: str = Field(..., example="e1479787-7c18-4072-9d16-04ac7082fef9")
    user_message: ChatMessage
    assistant_message: ChatMessage
    context_chunks: List[str] = Field(
        default=[], 
        description="RAG context chunks used for generating the response",
        example=["Section 80. Notice. (1) Save as otherwise provided...", "The tenant shall be liable..."]
    )


class SessionListItem(BaseModel):
    """Schema for session list items."""
    id: str = Field(..., example="e1479787-7c18-4072-9d16-04ac7082fef9")
    title: str = Field(..., example="Legal Query - Tenant Rights")
    created_at: datetime = Field(..., example="2026-01-04T10:30:00")
    updated_at: datetime = Field(..., example="2026-01-04T10:35:00")
    message_count: Optional[int] = Field(0, example=4)

    model_config = ConfigDict(from_attributes=True)
