"""
Pydantic schemas for Document Templates and Generation.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
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
    field_name: str = Field(..., example="complainant_name")
    description: str = Field(..., example="Full name of the complainant")
    example: Optional[str] = Field(None, example="Raj Kumar Singh")
    required: bool = Field(True, example=True)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "field_name": "complainant_name",
                "description": "Full name of the complainant",
                "example": "Raj Kumar Singh",
                "required": True
            }
        }
    )


class DocumentTemplateBase(BaseModel):
    """Base schema for document templates."""
    name: str = Field(..., min_length=1, max_length=255, description="Template name", example="Consumer Complaint")
    description: Optional[str] = Field(None, description="Template description", example="Complaint for consumer protection issues - defective products, services, etc.")
    category: DocumentCategory = Field(DocumentCategory.OTHER, description="Document category", example="complaint")


class DocumentTemplateCreate(DocumentTemplateBase):
    """Schema for creating a new template."""
    template_content: str = Field(
        ..., 
        min_length=10, 
        description="Template content with placeholders like {{field_name}}",
        example="BEFORE THE CONSUMER FORUM\n\n{{complainant_name}}\nR/o {{complainant_address}}\n... COMPLAINANT\n\nVERSUS\n\n{{respondent_name}}\n{{respondent_address}}\n... OPPOSITE PARTY"
    )
    required_fields: List[str] = Field(
        default=[], 
        description="List of required field names",
        example=["complainant_name", "complainant_address", "respondent_name", "respondent_address"]
    )
    field_descriptions: Optional[List[TemplateFieldDescription]] = Field(None, description="Descriptions for each field")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Consumer Complaint",
                "description": "Complaint for consumer protection issues",
                "category": "complaint",
                "template_content": "BEFORE THE CONSUMER FORUM\n\n{{complainant_name}}\nR/o {{complainant_address}}\n... COMPLAINANT\n\nVERSUS\n\n{{respondent_name}}\n{{respondent_address}}\n... OPPOSITE PARTY",
                "required_fields": ["complainant_name", "complainant_address", "respondent_name", "respondent_address"],
                "field_descriptions": [
                    {"field_name": "complainant_name", "description": "Full name of the complainant", "required": True}
                ]
            }
        }
    )


class DocumentTemplateUpdate(BaseModel):
    """Schema for updating a template."""
    name: Optional[str] = Field(None, min_length=1, max_length=255, example="Updated Consumer Complaint")
    description: Optional[str] = Field(None, example="Updated description for consumer complaints")
    category: Optional[DocumentCategory] = Field(None, example="complaint")
    template_content: Optional[str] = Field(None, example="Updated template content...")
    required_fields: Optional[List[str]] = None
    field_descriptions: Optional[List[TemplateFieldDescription]] = None
    is_active: Optional[bool] = Field(None, example=True)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Updated Consumer Complaint",
                "description": "Updated description for consumer complaints"
            }
        }
    )


class DocumentTemplate(DocumentTemplateBase):
    """Schema for returning a template."""
    id: str = Field(..., example="a1b2c3d4-e5f6-7890-abcd-ef1234567890")
    template_content: str
    required_fields: List[str]
    field_descriptions: Optional[List[TemplateFieldDescription]] = None
    is_active: bool = Field(..., example=True)
    created_at: datetime = Field(..., example="2026-01-04T10:30:00")
    updated_at: datetime = Field(..., example="2026-01-04T10:30:00")
    created_by: Optional[int] = Field(None, example=1)

    model_config = ConfigDict(from_attributes=True)


class DocumentTemplateList(BaseModel):
    """Schema for template list item."""
    id: str = Field(..., example="a1b2c3d4-e5f6-7890-abcd-ef1234567890")
    name: str = Field(..., example="Consumer Complaint")
    description: Optional[str] = Field(None, example="Complaint for consumer protection issues")
    category: str = Field(..., example="complaint")
    is_active: bool = Field(..., example=True)
    created_at: datetime = Field(..., example="2026-01-04T10:30:00")

    model_config = ConfigDict(from_attributes=True)


# ============== Generation Schemas ==============

class DocumentGenerateRequest(BaseModel):
    """Schema for generating a document from template."""
    template_id: str = Field(..., description="UUID of the template to use", example="a1b2c3d4-e5f6-7890-abcd-ef1234567890")
    user_input: str = Field(
        ..., 
        min_length=10, 
        max_length=10000, 
        description="Free-form user description of the case/situation",
        example="I am Raj Kumar Singh residing at 123 MG Road, Delhi. I purchased a Samsung LED TV from XYZ Electronics on 15th June 2025 for Rs. 50,000. The TV stopped working after 2 days and the company is refusing to provide a refund or replacement."
    )
    additional_fields: Optional[Dict[str, str]] = Field(
        None, 
        description="Optional pre-filled field values",
        example={"court_name": "Delhi District Consumer Forum", "case_value": "50000"}
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "template_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "user_input": "I am Raj Kumar Singh residing at 123 MG Road, Delhi. I purchased a Samsung LED TV from XYZ Electronics on 15th June 2025 for Rs. 50,000. The TV stopped working after 2 days and the company is refusing to provide a refund or replacement.",
                "additional_fields": {"court_name": "Delhi District Consumer Forum"}
            }
        }
    )


class DocumentGenerateFromDescription(BaseModel):
    """Schema for generating a document from natural language description."""
    description: str = Field(
        ..., 
        min_length=20, 
        max_length=15000, 
        description="Natural language description of the legal matter",
        example="I want to file a legal notice against my employer who has been withholding my salary for the past 3 months. My name is Priya Sharma and I work at ABC Tech Solutions in Bangalore. They owe me Rs. 1,50,000 in unpaid salary."
    )
    category: Optional[DocumentCategory] = Field(None, description="Suggested document category", example="notice")
    title: Optional[str] = Field(None, description="Optional title for the document", example="Legal Notice for Salary Recovery")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "description": "I want to file a legal notice against my employer who has been withholding my salary for the past 3 months. My name is Priya Sharma and I work at ABC Tech Solutions in Bangalore. They owe me Rs. 1,50,000 in unpaid salary.",
                "category": "notice",
                "title": "Legal Notice for Salary Recovery"
            }
        }
    )


class ExtractedField(BaseModel):
    """A field extracted from user input."""
    field_name: str = Field(..., example="complainant_name")
    value: str = Field(..., example="Raj Kumar Singh")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Confidence score 0-1", example=0.95)


class GeneratedDocumentResponse(BaseModel):
    """Schema for generated document response."""
    id: str = Field(..., example="b2c3d4e5-f6a7-8901-bcde-f23456789012")
    template_id: str = Field(..., example="a1b2c3d4-e5f6-7890-abcd-ef1234567890")
    title: str = Field(..., example="Consumer Complaint - Raj Kumar Singh")
    content: str = Field(..., example="BEFORE THE CONSUMER FORUM\n\nRaj Kumar Singh\nR/o 123 MG Road, Delhi\n... COMPLAINANT...")
    extracted_fields: List[ExtractedField] = Field(
        ...,
        example=[
            {"field_name": "complainant_name", "value": "Raj Kumar Singh", "confidence": 0.95},
            {"field_name": "complainant_address", "value": "123 MG Road, Delhi", "confidence": 0.90}
        ]
    )
    created_at: datetime = Field(..., example="2026-01-04T10:30:00")

    model_config = ConfigDict(from_attributes=True)


class GeneratedDocumentList(BaseModel):
    """Schema for listing generated documents."""
    id: str = Field(..., example="b2c3d4e5-f6a7-8901-bcde-f23456789012")
    template_id: str = Field(..., example="a1b2c3d4-e5f6-7890-abcd-ef1234567890")
    title: str = Field(..., example="Consumer Complaint - Raj Kumar Singh")
    created_at: datetime = Field(..., example="2026-01-04T10:30:00")

    model_config = ConfigDict(from_attributes=True)


class GeneratedDocumentDetail(GeneratedDocumentResponse):
    """Detailed view of generated document."""
    input_data: str = Field(..., example="I am Raj Kumar Singh residing at 123 MG Road...")
    updated_at: datetime = Field(..., example="2026-01-04T10:35:00")

    model_config = ConfigDict(from_attributes=True)
