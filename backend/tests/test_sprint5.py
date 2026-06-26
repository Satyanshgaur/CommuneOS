import pytest
import io
import sys
import os
from fastapi.testclient import TestClient

# Add backend to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from services.db import (
    users_table, community_members_table, documents_table, documents_storage
)

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_sprint5_test_data():
    """Seed test users, memberships, and clean up documents."""
    users_table.clear()
    community_members_table.clear()
    documents_table.clear()
    documents_storage.clear()

    # 1. Create a GPU user
    users_table["gpu_user"] = {
        "user_id": "gpu_user",
        "username": "gpu_user",
        "email": "gpu@test.com",
        "bio": "GPU Dev",
        "skills": {"CUDA": 4}
    }
    community_members_table["gpu_user"] = {
        "user_id": "gpu_user",
        "community_id": "comm-gpu",
        "role_id": "role-member"
    }

    # 2. Create an ML user
    users_table["ml_user"] = {
        "user_id": "ml_user",
        "username": "ml_user",
        "email": "ml@test.com",
        "bio": "ML Dev",
        "skills": {"PyTorch": 4}
    }
    community_members_table["ml_user"] = {
        "user_id": "ml_user",
        "community_id": "comm-ml",
        "role_id": "role-member"
    }

def test_upload_document_success():
    """POST /api/v1/documents successfully uploads a valid document."""
    file_data = b"Hello, this is a test document."
    file_obj = io.BytesIO(file_data)
    
    response = client.post(
        "/api/v1/documents",
        headers={"X-User-Id": "gpu_user"},
        data={
            "title": "CUDA Coalescing Guide",
            "description": "A guide about coalesced memory access.",
            "category": "Documentation"
        },
        files={"file": ("coalescing.txt", file_obj, "text/plain")}
    )
    
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    
    metadata = res_data["data"]
    assert metadata["title"] == "CUDA Coalescing Guide"
    assert metadata["description"] == "A guide about coalesced memory access."
    assert metadata["category"] == "Documentation"
    assert metadata["uploaded_by"] == "gpu_user"
    assert metadata["file_size"] == len(file_data)
    assert metadata["file_type"] == "txt"
    assert metadata["community_id"] == "comm-gpu"
    assert "document_id" in metadata

    # Check store
    doc_id = metadata["document_id"]
    assert doc_id in documents_table
    assert documents_storage[doc_id] == file_data

def test_upload_document_invalid_type():
    """POST /api/v1/documents rejects unsupported file types."""
    file_data = b"binary_data"
    file_obj = io.BytesIO(file_data)
    
    response = client.post(
        "/api/v1/documents",
        headers={"X-User-Id": "gpu_user"},
        data={
            "title": "Bad Script",
            "category": "Script"
        },
        files={"file": ("script.exe", file_obj, "application/octet-stream")}
    )
    
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]

def test_upload_document_exceeds_size():
    """POST /api/v1/documents rejects files exceeding 5MB."""
    # Create 5.1 MB of data
    large_data = b"a" * (5 * 1024 * 1024 + 100)
    file_obj = io.BytesIO(large_data)
    
    response = client.post(
        "/api/v1/documents",
        headers={"X-User-Id": "gpu_user"},
        data={
            "title": "Large File",
            "category": "Raw"
        },
        files={"file": ("large.pdf", file_obj, "application/pdf")}
    )
    
    assert response.status_code == 400
    assert "File size exceeds the 5MB limit" in response.json()["detail"]

def test_get_documents_and_search_filter():
    """GET /api/v1/documents lists, searches, and filters documents scoped to the community."""
    # Seed 3 documents
    doc1_metadata = {
        "document_id": "doc-1",
        "title": "CUDA Optimization Techniques",
        "description": "Shared memory optimization",
        "category": "CUDA",
        "uploaded_by": "gpu_user",
        "upload_date": "2026-06-27T00:00:00Z",
        "file_size": 100,
        "file_type": "pdf",
        "community_id": "comm-gpu"
    }
    doc2_metadata = {
        "document_id": "doc-2",
        "title": "Introduction to PyTorch Tensors",
        "description": "PyTorch basics",
        "category": "PyTorch",
        "uploaded_by": "ml_user",
        "upload_date": "2026-06-27T00:00:00Z",
        "file_size": 200,
        "file_type": "docx",
        "community_id": "comm-ml"
    }
    doc3_metadata = {
        "document_id": "doc-3",
        "title": "GPU Hardware Architecture AMA",
        "description": "NVIDIA architecture FAQ",
        "category": "Hardware",
        "uploaded_by": "gpu_user",
        "upload_date": "2026-06-27T00:00:00Z",
        "file_size": 300,
        "file_type": "pptx",
        "community_id": "comm-gpu"
    }

    documents_table["doc-1"] = doc1_metadata
    documents_table["doc-2"] = doc2_metadata
    documents_table["doc-3"] = doc3_metadata

    # 1. Query as GPU user
    response = client.get("/api/v1/documents", headers={"X-User-Id": "gpu_user"})
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    docs = res_data["data"]["documents"]
    # Should only return doc-1 and doc-3 (comm-gpu)
    assert len(docs) == 2
    assert any(d["document_id"] == "doc-1" for d in docs)
    assert any(d["document_id"] == "doc-3" for d in docs)

    # 2. Search GPU documents by title
    response = client.get("/api/v1/documents?search=techniques", headers={"X-User-Id": "gpu_user"})
    docs = response.json()["data"]["documents"]
    assert len(docs) == 1
    assert docs[0]["document_id"] == "doc-1"

    # 3. Filter GPU documents by category
    response = client.get("/api/v1/documents?category=hardware", headers={"X-User-Id": "gpu_user"})
    docs = response.json()["data"]["documents"]
    assert len(docs) == 1
    assert docs[0]["document_id"] == "doc-3"

    # 4. Query as ML user
    response = client.get("/api/v1/documents", headers={"X-User-Id": "ml_user"})
    docs = response.json()["data"]["documents"]
    # Should only return doc-2 (comm-ml)
    assert len(docs) == 1
    assert docs[0]["document_id"] == "doc-2"

def test_download_document_and_isolation():
    """GET /api/v1/documents/{id} serves the document file and enforces tenant isolation."""
    doc_metadata = {
        "document_id": "doc-1",
        "title": "CUDA Optimization Techniques",
        "category": "CUDA",
        "uploaded_by": "gpu_user",
        "upload_date": "2026-06-27T00:00:00Z",
        "file_size": 12,
        "file_type": "pdf",
        "community_id": "comm-gpu"
    }
    documents_table["doc-1"] = doc_metadata
    documents_storage["doc-1"] = b"PDF_CONTENT_"

    # 1. Download as GPU user (success)
    response = client.get("/api/v1/documents/doc-1", headers={"X-User-Id": "gpu_user"})
    assert response.status_code == 200
    assert response.content == b"PDF_CONTENT_"
    assert response.headers["content-type"] == "application/pdf"
    assert "attachment" in response.headers["content-disposition"]
    assert "CUDA Optimization Techniques.pdf" in response.headers["content-disposition"]

    # 2. Attempt download as ML user (403 Forbidden - cross access)
    response = client.get("/api/v1/documents/doc-1", headers={"X-User-Id": "ml_user"})
    assert response.status_code == 403
    assert "Cannot access another community" in response.json()["detail"]

    # 3. Attempt download of non-existent document
    response = client.get("/api/v1/documents/doc-missing", headers={"X-User-Id": "gpu_user"})
    assert response.status_code == 404

def test_delete_document_and_isolation():
    """DELETE /api/v1/documents/{id} deletes the document and enforces tenant isolation."""
    doc_metadata = {
        "document_id": "doc-1",
        "title": "CUDA Optimization Techniques",
        "category": "CUDA",
        "uploaded_by": "gpu_user",
        "upload_date": "2026-06-27T00:00:00Z",
        "file_size": 12,
        "file_type": "pdf",
        "community_id": "comm-gpu"
    }
    documents_table["doc-1"] = doc_metadata
    documents_storage["doc-1"] = b"PDF_CONTENT_"

    # 1. Attempt delete as ML user (403 Forbidden - cross access)
    response = client.delete("/api/v1/documents/doc-1", headers={"X-User-Id": "ml_user"})
    assert response.status_code == 403
    assert "Cannot delete another community" in response.json()["detail"]
    assert "doc-1" in documents_table

    # 2. Delete as GPU user (success)
    response = client.delete("/api/v1/documents/doc-1", headers={"X-User-Id": "gpu_user"})
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "doc-1" not in documents_table
    assert "doc-1" not in documents_storage
