"""
Chat API endpoints - Production-ready with UUID sessions and RAG context.
"""
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.services.rag_service import rag_service
from app.services.llm_service import llm_service
from app.schemas.response import StandardResponse

router = APIRouter()


@router.post("/send", response_model=StandardResponse, summary="Send a chat message")
def send_message(
    *,
    db: Session = Depends(deps.get_db),
    chat_in: schemas.chat.ChatRequest,
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    **Send a message and get AI response with RAG context.**

    This endpoint handles the chat interaction with RAG-powered AI.
    
    - **message**: The user's message/question (1-10000 characters).
    - **session_id**: (Optional) Existing session UUID. If not provided, creates a new session.
    
    Returns the AI response along with the RAG context chunks used.
    """
    # Validate and get or create session
    session = None
    if chat_in.session_id:
        session = crud.crud_chat.chat_session.get(db, id=chat_in.session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        if session.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this chat session"
            )
    else:
        # Create new session with first message as title (truncated)
        title = chat_in.message[:50] + "..." if len(chat_in.message) > 50 else chat_in.message
        session = crud.crud_chat.chat_session.create(
            db, user_id=current_user.id, title=title
        )
    
    # Save user message
    user_msg = crud.crud_chat.chat_message.create(
        db, session_id=session.id, role="user", content=chat_in.message
    )
    
    # Get chat history for context (exclude current message)
    history_messages = crud.crud_chat.chat_message.get_by_session(db, session_id=session.id)
    chat_history = [
        {"role": msg.role, "content": msg.content} 
        for msg in history_messages[:-1]
    ]
    
    # Search RAG for relevant context
    context_chunks = rag_service.search(chat_in.message, k=4)
    
    # Generate AI response
    ai_response = llm_service.generate_response(
        user_message=chat_in.message,
        context=context_chunks,
        chat_history=chat_history
    )
    
    # Save assistant message with context
    assistant_msg = crud.crud_chat.chat_message.create(
        db, 
        session_id=session.id, 
        role="assistant", 
        content=ai_response,
        context_chunks=context_chunks
    )
    
    return {
        "message": "Message sent successfully",
        "data": {
            "session_id": session.id,
            "user_message": {
                "id": user_msg.id,
                "role": user_msg.role,
                "content": user_msg.content,
                "created_at": user_msg.created_at.isoformat()
            },
            "assistant_message": {
                "id": assistant_msg.id,
                "role": assistant_msg.role,
                "content": assistant_msg.content,
                "created_at": assistant_msg.created_at.isoformat()
            },
            "context_chunks": context_chunks
        }
    }


@router.get("/sessions", response_model=StandardResponse, summary="Get all chat sessions")
def get_sessions(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0, description="Number of sessions to skip"),
    limit: int = Query(50, ge=1, le=100, description="Max sessions to return"),
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    **Get all chat sessions for the current user.**
    
    Returns a list of chat sessions ordered by most recent first.
    Includes message count for each session.
    """
    sessions = crud.crud_chat.chat_session.get_by_user(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    
    sessions_data = [
        {
            "id": s.id,
            "title": s.title,
            "created_at": s.created_at.isoformat(),
            "updated_at": s.updated_at.isoformat(),
            "message_count": len(s.messages) if s.messages else 0
        }
        for s in sessions
    ]
    
    return {
        "message": "Sessions retrieved successfully",
        "data": sessions_data
    }


@router.get("/sessions/{session_id}", response_model=StandardResponse, summary="Get a chat session")
def get_session(
    session_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    **Get a specific chat session with all messages.**
    
    Returns the session details along with the complete message history.
    """
    session = crud.crud_chat.chat_session.get(db, id=session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this chat session"
        )
    
    messages = crud.crud_chat.chat_message.get_by_session(db, session_id=session_id)
    
    return {
        "message": "Session retrieved successfully",
        "data": {
            "id": session.id,
            "title": session.title,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "messages": [
                {
                    "id": m.id,
                    "role": m.role,
                    "content": m.content,
                    "created_at": m.created_at.isoformat(),
                    "context_chunks": crud.crud_chat.chat_message.get_context_chunks(m) if m.role == "assistant" else None
                }
                for m in messages
            ]
        }
    }


@router.put("/sessions/{session_id}", response_model=StandardResponse, summary="Update a chat session")
def update_session(
    session_id: str,
    session_update: schemas.chat.ChatSessionUpdate,
    db: Session = Depends(deps.get_db),
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    **Update a chat session (e.g., rename it).**
    """
    session = crud.crud_chat.chat_session.get(db, id=session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this chat session"
        )
    
    updated = crud.crud_chat.chat_session.update_title(
        db, db_obj=session, title=session_update.title
    )
    
    return {
        "message": "Session updated successfully",
        "data": {
            "id": updated.id,
            "title": updated.title,
            "updated_at": updated.updated_at.isoformat()
        }
    }


@router.delete("/sessions/{session_id}", response_model=StandardResponse, summary="Delete a chat session")
def delete_session(
    session_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    **Delete a chat session and all its messages.**
    """
    session = crud.crud_chat.chat_session.get(db, id=session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this chat session"
        )
    
    crud.crud_chat.chat_session.delete(db, id=session_id)
    
    return {
        "message": "Session deleted successfully",
        "data": []
    }


@router.post("/rebuild-index", response_model=StandardResponse, summary="Rebuild RAG index")
def rebuild_rag_index(
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    **Rebuild the RAG index from documents.**
    
    Use this after adding new documents to the `docs` folder.
    This operation may take some time depending on the number of documents.
    """
    success = rag_service.rebuild_index()
    
    if success:
        return {
            "message": "RAG index rebuilt successfully",
            "data": []
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to rebuild RAG index"
        )
