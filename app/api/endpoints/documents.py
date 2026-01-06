"""
Document Generator API Endpoints - Complaint & Petition Generator.
"""
import json
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.services.document_service import document_generator
from app.schemas.response import StandardResponse
from app.schemas.document import (
    DocumentTemplateCreate, 
    DocumentTemplateUpdate,
    DocumentGenerateRequest,
    DocumentGenerateFromDescription,
    DocumentCategory
)

router = APIRouter()


# ============== Template Endpoints ==============

@router.get("/templates", response_model=StandardResponse, summary="List all templates")
def list_templates(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    category: Optional[str] = Query(None, description="Filter by category"),
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    **Get all available document templates.**
    
    Optionally filter by category: complaint, petition, application, notice, affidavit, agreement, other
    """
    templates = crud.crud_document.document_template.get_all(
        db, skip=skip, limit=limit, category=category, active_only=True
    )
    
    templates_data = [
        {
            "id": t.id,
            "name": t.name,
            "description": t.description,
            "category": t.category,
            "required_fields": crud.crud_document.document_template.get_required_fields(t),
            "created_at": t.created_at.isoformat()
        }
        for t in templates
    ]
    
    return {
        "message": f"Found {len(templates_data)} templates",
        "data": templates_data
    }


@router.get("/templates/{template_id}", response_model=StandardResponse, summary="Get template details")
def get_template(
    template_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    **Get a specific template with full details including content.**
    """
    template = crud.crud_document.document_template.get(db, id=template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    return {
        "message": "Template retrieved successfully",
        "data": {
            "id": template.id,
            "name": template.name,
            "description": template.description,
            "category": template.category,
            "template_content": template.template_content,
            "required_fields": crud.crud_document.document_template.get_required_fields(template),
            "field_descriptions": crud.crud_document.document_template.get_field_descriptions(template),
            "is_active": template.is_active,
            "created_at": template.created_at.isoformat(),
            "updated_at": template.updated_at.isoformat()
        }
    }


@router.post("/templates", response_model=StandardResponse, status_code=status.HTTP_201_CREATED, summary="Create template")
def create_template(
    template_in: DocumentTemplateCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    **Create a new document template.**
    
    Template content should use {{field_name}} placeholders.
    """
    # Check for duplicate name
    existing = crud.crud_document.document_template.get_by_name(db, name=template_in.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A template with this name already exists"
        )
    
    field_descriptions = None
    if template_in.field_descriptions:
        field_descriptions = [fd.model_dump() for fd in template_in.field_descriptions]
    
    template = crud.crud_document.document_template.create(
        db,
        name=template_in.name,
        description=template_in.description,
        category=template_in.category.value,
        template_content=template_in.template_content,
        required_fields=template_in.required_fields,
        field_descriptions=field_descriptions,
        created_by=current_user.id
    )
    
    return {
        "message": "Template created successfully",
        "data": {
            "id": template.id,
            "name": template.name,
            "category": template.category,
            "created_at": template.created_at.isoformat()
        }
    }


@router.put("/templates/{template_id}", response_model=StandardResponse, summary="Update template")
def update_template(
    template_id: str,
    template_update: DocumentTemplateUpdate,
    db: Session = Depends(deps.get_db),
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    **Update an existing template.**
    """
    template = crud.crud_document.document_template.get(db, id=template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    update_data = template_update.model_dump(exclude_unset=True)
    if "category" in update_data and update_data["category"]:
        update_data["category"] = update_data["category"].value
    if "field_descriptions" in update_data and update_data["field_descriptions"]:
        update_data["field_descriptions"] = [fd.model_dump() if hasattr(fd, 'model_dump') else fd for fd in update_data["field_descriptions"]]
    
    updated = crud.crud_document.document_template.update(db, db_obj=template, update_data=update_data)
    
    return {
        "message": "Template updated successfully",
        "data": {
            "id": updated.id,
            "name": updated.name,
            "updated_at": updated.updated_at.isoformat()
        }
    }


@router.delete("/templates/{template_id}", response_model=StandardResponse, summary="Delete template")
def delete_template(
    template_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    **Delete a template.**
    """
    template = crud.crud_document.document_template.get(db, id=template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    crud.crud_document.document_template.delete(db, id=template_id)
    
    return {
        "message": "Template deleted successfully",
        "data": []
    }


# ============== Document Generation Endpoints ==============

@router.post("/generate", response_model=StandardResponse, summary="Generate document from template")
def generate_document(
    request: DocumentGenerateRequest,
    db: Session = Depends(deps.get_db),
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    **Generate a document from a template using user's input.**
    
    The system will:
    1. Extract required information from user's description
    2. Fill the template placeholders
    3. Save and return the generated document
    """
    # Get template
    template = crud.crud_document.document_template.get(db, id=request.template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    required_fields = crud.crud_document.document_template.get_required_fields(template)
    field_descriptions = crud.crud_document.document_template.get_field_descriptions(template)
    
    # Extract fields from user input
    extracted_values, extraction_details = document_generator.extract_fields_from_input(
        user_input=request.user_input,
        required_fields=required_fields,
        field_descriptions=field_descriptions
    )
    
    # Merge with any additional fields provided
    if request.additional_fields:
        extracted_values.update(request.additional_fields)
    
    # Fill template
    filled_content, missing_fields = document_generator.fill_template(
        template_content=template.template_content,
        field_values=extracted_values,
        required_fields=required_fields
    )
    
    # Generate title
    title = f"{template.name} - {extracted_values.get('petitioner_name', extracted_values.get('complainant_name', 'Generated'))}"
    
    # Save generated document
    generated_doc = crud.crud_document.generated_document.create(
        db,
        template_id=template.id,
        user_id=current_user.id,
        title=title,
        content=filled_content,
        input_data=request.user_input,
        extracted_fields=extraction_details
    )
    
    return {
        "message": "Document generated successfully",
        "data": {
            "id": generated_doc.id,
            "template_id": template.id,
            "template_name": template.name,
            "title": title,
            "content": filled_content,
            "extracted_fields": extraction_details,
            "missing_fields": missing_fields,
            "created_at": generated_doc.created_at.isoformat()
        }
    }


@router.post("/generate-free", response_model=StandardResponse, summary="Generate document from description")
def generate_document_free(
    request: DocumentGenerateFromDescription,
    db: Session = Depends(deps.get_db),
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    **Generate a complete legal document from natural language description.**
    
    No template required - AI generates the document directly based on your description.
    """
    category = request.category.value if request.category else None
    
    # Generate document using LLM
    result = document_generator.generate_document_from_description(
        description=request.description,
        category=category,
        title=request.title
    )
    
    # Find or create a "custom" template for storage
    custom_template = crud.crud_document.document_template.get_by_name(db, name="Custom Generated")
    if not custom_template:
        custom_template = crud.crud_document.document_template.create(
            db,
            name="Custom Generated",
            description="Template for AI-generated custom documents",
            category="other",
            template_content="{{content}}",
            required_fields=["content"],
            created_by=current_user.id
        )
    
    # Save generated document
    generated_doc = crud.crud_document.generated_document.create(
        db,
        template_id=custom_template.id,
        user_id=current_user.id,
        title=result["title"],
        content=result["content"],
        input_data=request.description,
        extracted_fields=[{"field_name": "category", "value": result["category"]}]
    )
    
    return {
        "message": "Document generated successfully",
        "data": {
            "id": generated_doc.id,
            "title": result["title"],
            "category": result["category"],
            "content": result["content"],
            "created_at": generated_doc.created_at.isoformat()
        }
    }


# ============== Generated Documents Management ==============

@router.get("/my-documents", response_model=StandardResponse, summary="List my generated documents")
def list_my_documents(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    **Get all documents generated by the current user.**
    """
    documents = crud.crud_document.generated_document.get_by_user(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    
    docs_data = [
        {
            "id": d.id,
            "template_id": d.template_id,
            "title": d.title,
            "created_at": d.created_at.isoformat(),
            "updated_at": d.updated_at.isoformat()
        }
        for d in documents
    ]
    
    return {
        "message": f"Found {len(docs_data)} documents",
        "data": docs_data
    }


@router.get("/my-documents/{document_id}", response_model=StandardResponse, summary="Get generated document")
def get_my_document(
    document_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    **Get a specific generated document with full content.**
    """
    document = crud.crud_document.generated_document.get(db, id=document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    if document.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this document"
        )
    
    extracted_fields = crud.crud_document.generated_document.get_extracted_fields(document)
    
    return {
        "message": "Document retrieved successfully",
        "data": {
            "id": document.id,
            "template_id": document.template_id,
            "title": document.title,
            "content": document.content,
            "input_data": document.input_data,
            "extracted_fields": extracted_fields,
            "created_at": document.created_at.isoformat(),
            "updated_at": document.updated_at.isoformat()
        }
    }


@router.put("/my-documents/{document_id}", response_model=StandardResponse, summary="Update generated document")
def update_my_document(
    document_id: str,
    title: Optional[str] = None,
    content: Optional[str] = None,
    db: Session = Depends(deps.get_db),
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    **Update a generated document's content or title.**
    """
    document = crud.crud_document.generated_document.get(db, id=document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    if document.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this document"
        )
    
    if content:
        updated = crud.crud_document.generated_document.update_content(
            db, db_obj=document, content=content, title=title
        )
    elif title:
        document.title = title
        db.add(document)
        db.commit()
        db.refresh(document)
        updated = document
    else:
        updated = document
    
    return {
        "message": "Document updated successfully",
        "data": {
            "id": updated.id,
            "title": updated.title,
            "updated_at": updated.updated_at.isoformat()
        }
    }


@router.delete("/my-documents/{document_id}", response_model=StandardResponse, summary="Delete generated document")
def delete_my_document(
    document_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    **Delete a generated document.**
    """
    document = crud.crud_document.generated_document.get(db, id=document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    if document.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this document"
        )
    
    crud.crud_document.generated_document.delete(db, id=document_id)
    
    return {
        "message": "Document deleted successfully",
        "data": []
    }


@router.post("/suggest-template", response_model=StandardResponse, summary="Suggest template for description")
def suggest_template(
    description: str = Query(..., min_length=10, description="Description of your legal matter"),
    db: Session = Depends(deps.get_db),
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    **Get template suggestions based on your description.**
    
    AI analyzes your description and suggests the most appropriate template.
    """
    templates = crud.crud_document.document_template.get_all(db, active_only=True)
    
    if not templates:
        return {
            "message": "No templates available",
            "data": {"suggested_template": None, "available_templates": []}
        }
    
    templates_info = [
        {
            "id": t.id,
            "name": t.name,
            "category": t.category,
            "description": t.description
        }
        for t in templates
    ]
    
    suggested_id = document_generator.suggest_template(description, templates_info)
    
    suggested_template = None
    if suggested_id:
        for t in templates_info:
            if t["id"] == suggested_id:
                suggested_template = t
                break
    
    return {
        "message": "Template suggestion generated",
        "data": {
            "suggested_template": suggested_template,
            "available_templates": templates_info
        }
    }
