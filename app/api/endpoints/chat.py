"""
Chat API endpoints - Production-ready with UUID sessions and RAG context.
"""
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
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
    context_chunks = []
    
    # If document_id is provided, limit search to that document
    if chat_in.document_id:
        # Verify document exists and belongs to user
        doc = db.query(models.uploaded_document.UploadedDocument).filter(
            models.uploaded_document.UploadedDocument.id == chat_in.document_id
        ).first()
        
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        if doc.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this document"
            )
            
        # Ensure index exists for this document
        # We might need to create it if it doesn't exist (e.g. first time chat)
        # Note: Ideally this should happen on upload, but for now we do it lazily or check here
        rag_service.create_index_for_document(doc.file_path, doc.id)
        
        context_chunks = rag_service.search(chat_in.message, k=4, document_id=chat_in.document_id)
    else:
        # Default global search
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


@router.post("/test-search", response_model=StandardResponse, summary="Test RAG search with scores")
def test_rag_search(
    query: str = Query(..., min_length=1, description="Search query to test"),
    k: int = Query(6, ge=1, le=20, description="Number of chunks to retrieve"),
    threshold: float = Query(0.7, ge=0.0, le=1.0, description="Minimum relevance score (0-1)"),
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    **Test RAG search and see relevance scores.**
    
    This is a debug endpoint to help you understand how relevant the retrieved chunks are.
    
    - **query**: The search query
    - **k**: Number of chunks to retrieve (before filtering)
    - **threshold**: Minimum similarity score (0-1). Higher = stricter.
    
    Returns chunks with their similarity scores so you can tune the threshold.
    """
    # Get results with scores
    results_with_scores = rag_service.search_with_scores(query, k=k)
    
    # Also get filtered results
    filtered_results = rag_service.search(query, k=k, relevance_threshold=threshold)
    
    return {
        "message": f"Found {len(results_with_scores)} chunks, {len(filtered_results)} passed threshold",
        "data": {
            "query": query,
            "threshold": threshold,
            "total_chunks": len(results_with_scores),
            "filtered_chunks": len(filtered_results),
            "results": results_with_scores
        }
    }


@router.post("/upload", response_model=StandardResponse, summary="Upload document for chat")
def upload_chat_document(
    file: UploadFile = File(...),
    session_id: str = Query(None, description="Optional session ID to link"),
    db: Session = Depends(deps.get_db),
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    **Upload a document specifically for chat context.**
    
    This endpoint:
    1. Uploads the file.
    2. Creates a DB record.
    3. IMMEDIATELY triggers RAG indexing for this specific document.
    4. Returns the `document_id` to be used in `/chat/send`.
    """
    # 1. Validation
    if file.content_type not in ["application/pdf", "image/jpeg", "image/png", "text/plain"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only PDF, Images, and Text are allowed."
        )
        
    # 2. Save file
    import os
    import shutil
    import uuid
    from app.api.endpoints.uploads import UPLOAD_DIR # Reuse constants
    
    file_ext = os.path.splitext(file.filename)[1]
    safe_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save file: {str(e)}"
        )
        
    # 3. Create DB Record
    file_size = os.path.getsize(file_path)
    uploaded_doc = models.uploaded_document.UploadedDocument(
        filename=file.filename,
        file_path=file_path,
        file_type=file.content_type,
        file_size=file_size,
        user_id=current_user.id
    )
    db.add(uploaded_doc)
    db.commit()
    db.refresh(uploaded_doc)
    
    # 4. Trigger Indexing Immediately
    index_success = rag_service.create_index_for_document(file_path, uploaded_doc.id)
    
    if not index_success:
        # Note: We don't fail the upload, but we warn via a flag or log
        # In a real app, maybe returning a warning in response
        pass
        
    return {
        "message": "Document uploaded and processed for chat.",
        "data": {
            "document_id": uploaded_doc.id,
            "filename": uploaded_doc.filename,
            "indexing_status": "success" if index_success else "failed",
            "session_id": session_id # Echo back if useful
        }
    }
