from typing import Optional
from pydantic import BaseModel, Field

class DocumentMetadata(BaseModel):
    document_id: str = Field(..., description="Unique document ID")
    title: str = Field(..., description="Title of the document")
    description: Optional[str] = Field(None, description="Short description of the document")
    category: str = Field(..., description="Category of the document")
    uploaded_by: str = Field(..., description="User ID of the uploader")
    upload_date: str = Field(..., description="Date uploaded (ISO format)")
    file_size: int = Field(..., description="File size in bytes")
    file_type: str = Field(..., description="File type (e.g. pdf, docx, pptx, txt)")
    community_id: str = Field(..., description="Community ID of the document")
