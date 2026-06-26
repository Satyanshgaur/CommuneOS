from datetime import datetime, timezone
import uuid
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File, Form
from fastapi.responses import Response

from api.v1.dependencies import get_request_id
from services.db import documents_table, documents_storage
from utils.formatters import success_response
from utils.logger import get_logger

router = APIRouter(tags=["Community Documents"])
logger = get_logger("endpoint.documents")

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB size limit
SUPPORTED_EXTENSIONS = {"pdf", "docx", "pptx", "txt"}

@router.post("/documents")
async def upload_document(
    request: Request,
    title: str = Form(...),
    description: Optional[str] = Form(None),
    category: str = Form(...),
    file: UploadFile = File(...),
    request_id: str = Depends(get_request_id)
) -> Dict[str, Any]:
    """Upload a document to the community library."""
    user_id = request.state.user_id
    community_id = request.state.community_id

    filename = file.filename
    ext = filename.split(".")[-1].lower() if "." in filename else ""
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {ext or 'unknown'}. Supported types: PDF, DOCX, PPTX, TXT"
        )

    try:
        contents = await file.read()
        file_size = len(contents)
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds the 5MB limit. File is {round(file_size / (1024 * 1024), 2)}MB."
            )

        document_id = f"doc-{uuid.uuid4()}"
        metadata = {
            "document_id": document_id,
            "title": title,
            "description": description,
            "category": category,
            "uploaded_by": user_id,
            "upload_date": datetime.now(timezone.utc).isoformat(),
            "file_size": file_size,
            "file_type": ext,
            "community_id": community_id
        }

        # Store file data & metadata
        documents_table[document_id] = metadata
        documents_storage[document_id] = contents

        logger.info(f"User {user_id} uploaded document {document_id} ('{title}') to community {community_id}")

        return success_response(
            data=metadata,
            request_id=request_id,
            message=f"Document '{title}' uploaded successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload document: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during file upload."
        )

@router.get("/documents")
async def get_documents(
    request: Request,
    search: Optional[str] = None,
    category: Optional[str] = None,
    request_id: str = Depends(get_request_id)
) -> Dict[str, Any]:
    """Get all documents for the community, with optional search and filter."""
    community_id = request.state.community_id

    # Filter documents belonging to the resolved community
    docs = [doc for doc in documents_table.values() if doc.get("community_id") == community_id]

    # Apply search filter (case-insensitive substring match on title)
    if search:
        search_lower = search.lower()
        docs = [doc for doc in docs if search_lower in doc.get("title", "").lower()]

    # Apply category filter (exact match, case-insensitive)
    if category:
        category_lower = category.lower()
        docs = [doc for doc in docs if doc.get("category", "").lower() == category_lower]

    return success_response(
        data={"documents": docs, "count": len(docs)},
        request_id=request_id
    )

@router.get("/documents/{id}")
async def download_document(
    id: str,
    request: Request,
    request_id: str = Depends(get_request_id)
):
    """Download/retrieve a specific document from the community library."""
    community_id = request.state.community_id

    doc_metadata = documents_table.get(id)
    if not doc_metadata:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID '{id}' not found."
        )

    # Multi-tenant scoping validation
    if doc_metadata.get("community_id") != community_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Cannot access another community's documents."
        )

    file_contents = documents_storage.get(id)
    if not file_contents:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document content not found."
        )

    # Determine media type
    ext = doc_metadata.get("file_type", "")
    media_type = "application/octet-stream"
    if ext == "pdf":
        media_type = "application/pdf"
    elif ext == "txt":
        media_type = "text/plain"
    elif ext == "docx":
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif ext == "pptx":
        media_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"

    # Use title and extension for filename
    title = doc_metadata.get('title')
    filename = f"{title}.{ext}" if not title.lower().endswith(f".{ext}") else title

    # Return response as file download
    return Response(
        content=file_contents,
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename=\"{filename}\"",
            "X-Request-Id": request_id
        }
    )

@router.delete("/documents/{id}")
async def delete_document(
    id: str,
    request: Request,
    request_id: str = Depends(get_request_id)
) -> Dict[str, Any]:
    """Delete a document from the community library."""
    community_id = request.state.community_id

    doc_metadata = documents_table.get(id)
    if not doc_metadata:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID '{id}' not found."
        )

    # Multi-tenant scoping validation
    if doc_metadata.get("community_id") != community_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Cannot delete another community's documents."
        )

    # Remove from store
    documents_table.pop(id, None)
    documents_storage.pop(id, None)

    logger.info(f"User {request.state.user_id} deleted document {id} from community {community_id}")

    return success_response(
        data={"document_id": id, "deleted": True},
        request_id=request_id,
        message="Document deleted successfully"
    )
