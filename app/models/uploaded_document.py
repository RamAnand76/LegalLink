"""
Uploaded Document Model - Tracks files uploaded by users.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class UploadedDocument(Base):
    """
    Stores metadata for documents uploaded by users (PDFs, Images).
    """
    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)  # Path on disk
    file_type = Column(String(50), nullable=False)   # application/pdf, image/jpeg, etc.
    file_size = Column(Integer, nullable=True)       # Size in bytes
    
    # Analysis results (loophole detection etc) can be stored here or in a separate table/column
    analysis_result = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    
    # Relationships
    user = relationship("User", backref="uploaded_documents")
