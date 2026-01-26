"""
Pydantic schemas for Document Templates and Generation.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class DocumentCategory(str, Enum):
    """Categories of legal documents."""
    COMPLAINT = "complaint"
    PETITION = "petition"
    APPLICATION = "application"
    NOTICE = "notice"
    AFFIDAVIT = "affidavit"
    AGREEMENT = "agreement"
    OTHER = "other"


# ============== Template Schemas ==============

class TemplateFieldDescription(BaseModel):
    """Description of a template field."""
    field_name: str
    description: str
    example: Optional[str] = None
    required: bool = True


class DocumentTemplateBase(BaseModel):
    """Base schema for document templates."""
    name: str = Field(..., min_length=1, max_length=255, description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    category: DocumentCategory = Field(DocumentCategory.OTHER, description="Document category")


class DocumentTemplateCreate(DocumentTemplateBase):
    """Schema for creating a new template."""
    template_content: str = Field(..., min_length=10, description="Template content with placeholders like {{field_name}}")
    required_fields: List[str] = Field(default=[], description="List of required field names")
    field_descriptions: Optional[List[TemplateFieldDescription]] = Field(None, description="Descriptions for each field")


class DocumentTemplateUpdate(BaseModel):
    """Schema for updating a template."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[DocumentCategory] = None
    template_content: Optional[str] = None
    required_fields: Optional[List[str]] = None
    field_descriptions: Optional[List[TemplateFieldDescription]] = None
    is_active: Optional[bool] = None


class DocumentTemplate(DocumentTemplateBase):
    """Schema for returning a template."""
    id: str
    template_content: str
    required_fields: List[str]
    field_descriptions: Optional[List[TemplateFieldDescription]] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None

    class Config:
        from_attributes = True


class DocumentTemplateList(BaseModel):
    """Schema for template list item."""
    id: str
    name: str
    description: Optional[str]
    category: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============== Generation Schemas ==============

class DocumentGenerateRequest(BaseModel):
    """Schema for generating a document from template."""
    template_id: str = Field(..., description="UUID of the template to use")
    user_input: str = Field(..., min_length=10, max_length=10000, description="Free-form user description of the case/situation")
    additional_fields: Optional[Dict[str, str]] = Field(None, description="Optional pre-filled field values")


class DocumentGenerateFromDescription(BaseModel):
    """Schema for generating a document from natural language description."""
    description: str = Field(..., min_length=20, max_length=15000, description="Natural language description of the legal matter")
    category: Optional[DocumentCategory] = Field(None, description="Suggested document category")
    title: Optional[str] = Field(None, description="Optional title for the document")


class ExtractedField(BaseModel):
    """A field extracted from user input."""
    field_name: str
    value: str
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Confidence score 0-1")


class GeneratedDocumentResponse(BaseModel):
    """Schema for generated document response."""
    id: str
    template_id: str
    title: str
    content: str
    extracted_fields: List[ExtractedField]
    created_at: datetime

    class Config:
        from_attributes = True


class GeneratedDocumentList(BaseModel):
    """Schema for listing generated documents."""
    id: str
    template_id: str
    title: str
    created_at: datetime

    class Config:
        from_attributes = True


class GeneratedDocumentDetail(GeneratedDocumentResponse):
    """Detailed view of generated document."""
    input_data: str
    updated_at: datetime

    class Config:
        from_attributes = True


# ============== Upload & Analysis Schemas ==============

class DocumentUploadResponse(BaseModel):
    """Schema for document upload response."""
    id: str
    filename: str
    file_type: str
    file_size: int
    created_at: datetime

    class Config:
        from_attributes = True


class LoopholeAnalysisRequest(BaseModel):
    """Schema for requesting loophole analysis."""
    custom_instructions: Optional[str] = Field(None, description="Specific things to look for (e.g., 'termination clauses')")


class LoopholeAnalysisResponse(BaseModel):
    """Schema for loophole analysis results."""
    document_id: str
    analysis: str
    concerns: List[str] = Field(default=[], description="List of specific concerns identified")
    loopholes: List[str] = Field(default=[], description="List of potential loopholes found")
    created_at: datetime
