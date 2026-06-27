"""
CommuneOS Vector Database Service
Manages local ChromaDB collections for user resume memory and community knowledge base (mentors, resources, events).
"""
import os
import chromadb
from typing import List, Dict, Any, Optional
from utils.logger import get_logger

logger = get_logger("services.vector_db")

# Setup database path inside the backend directory
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "chroma_db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Global clients/collections
_client = None

def get_chroma_client():
    global _client
    if _client is None:
        logger.info(f"Initializing ChromaDB persistent client at: {DB_PATH}")
        _client = chromadb.PersistentClient(path=DB_PATH)
    return _client

def get_user_collection():
    client = get_chroma_client()
    return client.get_or_create_collection(
        name="user_memory",
        metadata={"hnsw:space": "cosine"}
    )

def get_community_collection():
    client = get_chroma_client()
    return client.get_or_create_collection(
        name="community_memory",
        metadata={"hnsw:space": "cosine"}
    )

def seed_community_database(force: bool = False):
    """Seed community memory database with mentors, resources, and events."""
    collection = get_community_collection()
    
    # Check if already seeded (by checking size)
    count = collection.count()
    if count > 0 and not force:
        logger.info(f"Community memory already contains {count} items. Skipping seed.")
        return

    logger.info("Seeding community memory collection...")
    
    # Import mock pools
    from services.mock_data import _mentor_pool_raw, _resource_pool_raw
    from utils.constants import COMMUNITY_CHANNELS
    
    documents = []
    metadatas = []
    ids = []

    # 1. Add Mentors
    for mentor in _mentor_pool_raw:
        doc = f"Mentor: {mentor['name']}. Role: {mentor['role']}. Expertise: {', '.join(mentor.get('expertise_areas', []))}."
        documents.append(doc)
        metadatas.append({
            "type": "mentor",
            "mentor_id": mentor["mentor_id"],
            "name": mentor["name"],
            "role": mentor["role"],
            "expertise": ",".join(mentor.get("expertise_areas", []))
        })
        ids.append(mentor["mentor_id"])

    # 2. Add Resources
    for res in _resource_pool_raw:
        doc = f"Resource: {res['title']}. Suitable for: {res['reason']}."
        documents.append(doc)
        metadatas.append({
            "type": "resource",
            "resource_id": res["resource_id"],
            "title": res["title"],
            "reason": res["reason"]
        })
        ids.append(res["resource_id"])

    # 3. Add Community Channels
    for ch in COMMUNITY_CHANNELS:
        doc = f"Community Channel: {ch['name']}. Topics: {', '.join(ch['topics'])}. Difficulty: {ch['difficulty']}."
        documents.append(doc)
        metadatas.append({
            "type": "channel",
            "channel_id": ch["id"],
            "name": ch["name"],
            "difficulty": ch["difficulty"]
        })
        ids.append(ch["id"])

    # 4. Add Community Events
    events = [
        {"id": "evt-001", "title": "GPU & CUDA AMA (Ask Me Anything)", "topics": ["CUDA", "GPU", "Systems Programming"], "description": "Live AMA with Sarah Jenkins, Principal GPU Engineer at NVIDIA. Learn CUDA tips and tricks."},
        {"id": "evt-002", "title": "Hands-on PyTorch Training Workshop", "topics": ["PyTorch", "ML", "Distributed Training"], "description": "Hands-on session with Amit Sharma, AI Infrastructure Lead, covering PyTorch distributed data parallel."},
        {"id": "evt-003", "title": "HFT C++ Systems Architecture Meetup", "topics": ["C++", "Low Latency", "HFT"], "description": "Tech talk with Alex Kowalski, HFT Systems Engineer, on lock-free queues and low latency C++ design."},
        {"id": "evt-004", "title": "Content Creators Hackathon & Video Editing Boot Camp", "topics": ["Video Editing", "YouTube", "Content Creation"], "description": "Join Zara Ahmed and Kai Nakamura to review video scripts, editing pipelines, and brand deals."},
    ]
    for evt in events:
        doc = f"Community Event: {evt['title']}. Description: {evt['description']}. Topics: {', '.join(evt['topics'])}."
        documents.append(doc)
        metadatas.append({
            "type": "event",
            "event_id": evt["id"],
            "title": evt["title"],
            "description": evt["description"]
        })
        ids.append(evt["id"])

    # 5. Add Community FAQs
    faqs = [
        {"id": "faq-001", "question": "How do I transition into AI Systems Engineering?", "answer": "You need a solid foundation in Linux, C++/Rust, computer architecture, and GPU programming (CUDA). Work on projects like writing custom kernels or distributed ML runtimes."},
        {"id": "faq-002", "question": "What is the best way to get CUDA mentorship?", "answer": "Join the GPU & Accelerators channel, attend the GPU AMA workshops, and request a 1:1 match with Sarah Jenkins or another advanced systems expert."},
    ]
    for faq in faqs:
        doc = f"Community FAQ. Question: {faq['question']} Answer: {faq['answer']}"
        documents.append(doc)
        metadatas.append({
            "type": "faq",
            "faq_id": faq["id"],
            "question": faq["question"],
            "answer": faq["answer"]
        })
        ids.append(faq["id"])

    # Perform Upsert
    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )
    logger.info(f"Community memory successfully seeded with {len(ids)} items.")

def add_user_resume_chunks(user_id: str, chunks: Dict[str, str]):
    """
    Store user resume chunks in user_memory collection.
    chunks is a dict like: {"Skills": "Python, CUDA", "Projects": "GraphRAG, CommunityOS", ...}
    """
    collection = get_user_collection()
    
    # First clear existing chunks for this user
    try:
        collection.delete(where={"user": user_id})
        logger.info(f"Cleared existing resume memory for user: {user_id}")
    except Exception as e:
        logger.debug(f"No existing chunks to clear for {user_id}: {e}")

    ids = []
    documents = []
    metadatas = []
    
    for section_name, section_text in chunks.items():
        if not section_text or len(section_text.strip()) == 0:
            continue
        chunk_id = f"resume_{user_id}_{section_name.lower().replace(' ', '_')}"
        doc = f"Section: {section_name}\nContent: {section_text}"
        
        ids.append(chunk_id)
        documents.append(doc)
        metadatas.append({
            "user": user_id,
            "source": "resume",
            "chunk": section_name
        })

    if ids:
        collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        logger.info(f"Uploaded {len(ids)} resume chunks to user_memory for {user_id}")
    else:
        logger.warning(f"No resume chunks to upload for {user_id}")

def query_user_memory(user_id: str, query_text: str, n_results: int = 3) -> List[Dict[str, Any]]:
    """Query user resume memory for matching chunks."""
    collection = get_user_collection()
    try:
        results = collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where={"user": user_id}
        )
        # Parse results into list of dicts
        items = []
        if results and "documents" in results and results["documents"]:
            docs = results["documents"][0]
            metas = results["metadatas"][0] if "metadatas" in results else [{}] * len(docs)
            dists = results["distances"][0] if "distances" in results else [0.0] * len(docs)
            for doc, meta, dist in zip(docs, metas, dists):
                items.append({
                    "document": doc,
                    "metadata": meta,
                    "distance": dist
                })
        return items
    except Exception as e:
        logger.error(f"Error querying user memory for {user_id}: {e}")
        return []

def query_community_memory(query_text: str, n_results: int = 5, filter_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """Query community memory for matching resources/mentors/events."""
    collection = get_community_collection()
    try:
        where_clause = None
        if filter_type:
            where_clause = {"type": filter_type}
            
        results = collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where=where_clause
        )
        items = []
        if results and "documents" in results and results["documents"]:
            docs = results["documents"][0]
            metas = results["metadatas"][0] if "metadatas" in results else [{}] * len(docs)
            dists = results["distances"][0] if "distances" in results else [0.0] * len(docs)
            for doc, meta, dist in zip(docs, metas, dists):
                items.append({
                    "document": doc,
                    "metadata": meta,
                    "distance": dist
                })
        return items
    except Exception as e:
        logger.error(f"Error querying community memory: {e}")
        return []
