"""
CRUD operations for Document Templates and Generated Documents.
"""
import json
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.document import DocumentTemplate, GeneratedDocument


class CRUDDocumentTemplate:
    """CRUD operations for document templates."""
    
    def create(
        self, 
        db: Session, 
        *, 
        name: str,
        template_content: str,
        required_fields: List[str],
        description: Optional[str] = None,
        category: str = "other",
        field_descriptions: Optional[List[dict]] = None,
        created_by: Optional[int] = None
    ) -> DocumentTemplate:
        """Create a new document template."""
        db_obj = DocumentTemplate(
            name=name,
            description=description,
            category=category,
            template_content=template_content,
            required_fields=json.dumps(required_fields),
            field_descriptions=json.dumps(field_descriptions) if field_descriptions else None,
            created_by=created_by
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: str) -> Optional[DocumentTemplate]:
        """Get a template by ID."""
        return db.query(DocumentTemplate).filter(DocumentTemplate.id == id).first()
    
    def get_by_name(self, db: Session, name: str) -> Optional[DocumentTemplate]:
        """Get a template by name."""
        return db.query(DocumentTemplate).filter(DocumentTemplate.name == name).first()
    
    def get_all(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 50,
        category: Optional[str] = None,
        active_only: bool = True
    ) -> List[DocumentTemplate]:
        """Get all templates with optional filtering."""
        query = db.query(DocumentTemplate)
        
        if active_only:
            query = query.filter(DocumentTemplate.is_active == True)
        
        if category:
            query = query.filter(DocumentTemplate.category == category)
        
        return query.order_by(DocumentTemplate.name).offset(skip).limit(limit).all()
    
    def get_by_category(self, db: Session, category: str) -> List[DocumentTemplate]:
        """Get all templates in a category."""
        return (
            db.query(DocumentTemplate)
            .filter(DocumentTemplate.category == category)
            .filter(DocumentTemplate.is_active == True)
            .order_by(DocumentTemplate.name)
            .all()
        )
    
    def update(
        self, 
        db: Session, 
        *, 
        db_obj: DocumentTemplate, 
        update_data: dict
    ) -> DocumentTemplate:
        """Update a template."""
        for field, value in update_data.items():
            if value is not None:
                if field == "required_fields":
                    setattr(db_obj, field, json.dumps(value))
                elif field == "field_descriptions":
                    setattr(db_obj, field, json.dumps(value) if value else None)
                else:
                    setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, *, id: str) -> bool:
        """Delete a template."""
        obj = db.query(DocumentTemplate).filter(DocumentTemplate.id == id).first()
        if obj:
            db.delete(obj)
            db.commit()
            return True
        return False
    
    def get_required_fields(self, template: DocumentTemplate) -> List[str]:
        """Parse and return required fields."""
        try:
            return json.loads(template.required_fields)
        except json.JSONDecodeError:
            return []
    
    def get_field_descriptions(self, template: DocumentTemplate) -> Optional[List[dict]]:
        """Parse and return field descriptions."""
        if template.field_descriptions:
            try:
                return json.loads(template.field_descriptions)
            except json.JSONDecodeError:
                return None
        return None


class CRUDGeneratedDocument:
    """CRUD operations for generated documents."""
    
    def create(
        self, 
        db: Session, 
        *, 
        template_id: str,
        user_id: int,
        title: str,
        content: str,
        input_data: str,
        extracted_fields: Optional[List[dict]] = None
    ) -> GeneratedDocument:
        """Create a new generated document."""
        db_obj = GeneratedDocument(
            template_id=template_id,
            user_id=user_id,
            title=title,
            content=content,
            input_data=input_data,
            extracted_fields=json.dumps(extracted_fields) if extracted_fields else None
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: str) -> Optional[GeneratedDocument]:
        """Get a generated document by ID."""
        return db.query(GeneratedDocument).filter(GeneratedDocument.id == id).first()
    
    def get_by_user(
        self, 
        db: Session, 
        *, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 50
    ) -> List[GeneratedDocument]:
        """Get all documents generated by a user."""
        return (
            db.query(GeneratedDocument)
            .filter(GeneratedDocument.user_id == user_id)
            .order_by(GeneratedDocument.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def update_content(
        self, 
        db: Session, 
        *, 
        db_obj: GeneratedDocument, 
        content: str,
        title: Optional[str] = None
    ) -> GeneratedDocument:
        """Update document content."""
        db_obj.content = content
        if title:
            db_obj.title = title
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, *, id: str) -> bool:
        """Delete a generated document."""
        obj = db.query(GeneratedDocument).filter(GeneratedDocument.id == id).first()
        if obj:
            db.delete(obj)
            db.commit()
            return True
        return False
    
    def get_extracted_fields(self, document: GeneratedDocument) -> List[dict]:
        """Parse and return extracted fields."""
        if document.extracted_fields:
            try:
                return json.loads(document.extracted_fields)
            except json.JSONDecodeError:
                return []
        return []


document_template = CRUDDocumentTemplate()
generated_document = CRUDGeneratedDocument()
