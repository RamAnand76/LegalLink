
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
    # document_id is passed in path parameter usually, but sometimes in body
    custom_instructions: Optional[str] = Field(None, description="Specific things to look for (e.g., 'termination clauses')")


class LoopholeAnalysisResponse(BaseModel):
    """Schema for loophole analysis results."""
    document_id: str
    analysis: str
    concerns: List[str] = Field(default=[], description="List of specific concerns identified")
    loopholes: List[str] = Field(default=[], description="List of potential loopholes found")
    created_at: datetime
