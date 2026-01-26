"""
Uploads API Endpoints - Handle file uploads and document analysis.
"""
import os
import shutil
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from app.core.config import settings

from app import crud, models, schemas
from app.api import deps
from app.schemas.response import StandardResponse

# We might need a service for analysis - placing placeholder here or importing if exists
# from app.services.analysis_service import analysis_service

router = APIRouter()

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@router.post("/upload", response_model=StandardResponse, summary="Upload a document")
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    **Upload a PDF or Image file.**
    
    Supported types: application/pdf, image/jpeg, image/png
    """
    if file.content_type not in ["application/pdf", "image/jpeg", "image/png"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only PDF and Images are allowed."
        )
    
    # Generate unique filename
    file_ext = os.path.splitext(file.filename)[1]
    import uuid
    safe_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    
    # Save file to disk
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save file: {str(e)}"
        )
        
    # Get file size
    file_size = os.path.getsize(file_path)
    
    # Create DB record
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
    
    return {
        "message": "File uploaded successfully",
        "data": {
            "id": uploaded_doc.id,
            "filename": uploaded_doc.filename,
            "file_type": uploaded_doc.file_type,
            "file_size": uploaded_doc.file_size,
            "created_at": uploaded_doc.created_at.isoformat()
        }
    }

@router.get("/", response_model=StandardResponse, summary="List uploaded documents")
def list_uploaded_documents(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    **Get all documents uploaded by the current user.**
    """
    # Assuming simple query since no specific CRUD for this yet
    docs = db.query(models.uploaded_document.UploadedDocument)\
        .filter(models.uploaded_document.UploadedDocument.user_id == current_user.id)\
        .offset(skip).limit(limit).all()
        
    docs_data = [
        {
            "id": d.id,
            "filename": d.filename,
            "file_type": d.file_type,
            "file_size": d.file_size,
            "created_at": d.created_at.isoformat()
        }
        for d in docs
    ]
    
    return {
        "message": f"Found {len(docs_data)} documents",
        "data": docs_data
    }

@router.get("/{document_id}", response_model=StandardResponse, summary="Get document details")
def get_document(
    document_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    **Get details of a specific uploaded document.**
    """
    doc = db.query(models.uploaded_document.UploadedDocument).filter(models.uploaded_document.UploadedDocument.id == document_id).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    if doc.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
        
    return {
        "message": "Document retrieved successfully",
        "data": {
            "id": doc.id,
            "filename": doc.filename,
            "file_type": doc.file_type,
            "file_size": doc.file_size,
            "analysis_result": doc.analysis_result, # Will be None initially
            "created_at": doc.created_at.isoformat()
        }
    }

@router.delete("/{document_id}", response_model=StandardResponse, summary="Delete document")
def delete_document(
    document_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    **Delete an uploaded document.**
    """
    doc = db.query(models.uploaded_document.UploadedDocument).filter(models.uploaded_document.UploadedDocument.id == document_id).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    if doc.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Delete file from disk
    if os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except Exception as e:
            # Log error but continue with DB deletion
            print(f"Error deleting file {doc.file_path}: {e}")
            
    db.delete(doc)
    db.commit()
    
    return {
        "message": "Document deleted successfully",
        "data": []
    }


@router.post("/{document_id}/analyze-loopholes", response_model=StandardResponse, summary="Analyze document for loopholes")
def analyze_document_loopholes(
    document_id: str,
    analysis_request: schemas.document.LoopholeAnalysisRequest,
    db: Session = Depends(deps.get_db),
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    **Analyze an uploaded document for loopholes and risks.**
    """
    # Get document
    doc = db.query(models.uploaded_document.UploadedDocument).filter(models.uploaded_document.UploadedDocument.id == document_id).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    if doc.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Check if we already have analysis (optional cache check)
    # For now, we allow re-analysis if requested
    
    # Import service here to avoid circular imports if any, or use the one from app/services/__init__
    from app.services.analysis_service import analysis_service
    
    # Perform analysis
    result = analysis_service.analyze_document(
        file_path=doc.file_path, 
        custom_instructions=analysis_request.custom_instructions
    )
    
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {result['error']}"
        )
        
    # Save result to DB
    import json
    doc.analysis_result = json.dumps(result)
    db.commit()
    
    return {
        "message": "Analysis completed successfully",
        "data": {
            "document_id": doc.id,
            "analysis": result.get("analysis", ""),
            "concerns": result.get("concerns", []),
            "loopholes": result.get("loopholes", []),
            "created_at": doc.created_at.isoformat() # Using doc creation time or we could add analyzed_at
        }
    }
