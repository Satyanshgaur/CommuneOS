# CommunityOS — Project Changelog & Migration Record

This changelog records the complete set of modifications, additions, and integrations implemented on **CommunityOS** to migrate from Supabase to a local FastAPI-driven architecture and establish a fully personalized **RAG (Retrieval Augmented Generation) pipeline**.

---

## 🔑 1. Complete Supabase-to-FastAPI Auth Migration

To make the application fully self-contained and run locally without requiring Supabase credentials:

- **Created Local Auth Endpoints** ([auth.py](file:///home/satyansh/communeos/backend/api/v1/endpoints/auth.py)):
  - Implemented `POST /api/auth/register` to register users locally, hash their passwords using `SHA256`, and save their records to `backend/data/users.json`.
  - Implemented `POST /api/auth/login-json` to validate credentials, generate a secure local token (`tok_...`), and persist active sessions in `backend/data/tokens.json`. Set default seed accounts (`rahul`, `priya`, `organizer`) to accept the password `"password"`.
  - Implemented `GET /api/auth/me` and `PUT /api/auth/me` to fetch and update user profiles via bearer token authentication.
- **Registered Auth Router**: Included the auth router under prefix `/api` in the main application router registration ([main.py](file:///home/satyansh/communeos/backend/main.py)).
- **Migrated Frontend Authentication** ([page.tsx](file:///home/satyansh/communeos/frontend/app/page.tsx)):
  - Removed all imports and lifecycle handlers referencing the client-side Supabase object.
  - Rewrote the `init` hook to fetch profile data from `/api/auth/me` using local token storage (`localStorage.getItem("communityos_token")`).
  - Rewrote `handleLogin`, `handleSignup`, and `handleLogout` to route HTTP calls directly to the local FastAPI backend.

---

## 🗄️ 2. ChromaDB RAG Vector Database Integration

- **Vector Database Service** ([vector_db.py](file:///home/satyansh/communeos/backend/services/vector_db.py)):
  - Initialized a persistent local ChromaDB instance under `backend/data/chroma_db`.
  - Created two collections: `user_memory` (semantic resume sections) and `community_memory` (events, guides, mentors, channels, resources, FAQs).
  - Wired community data catalogs to automatically embed and seed into ChromaDB on backend startup ([main.py](file:///home/satyansh/communeos/backend/main.py)).
  - Implemented cosine-similarity query helpers to retrieve resources, mentors, and events semantically.

---

## 📄 3. PDF Resume Extraction & Processing

- **Ingestion Service** ([resume_service.py](file:///home/satyansh/communeos/backend/services/resume_service.py)):
  - Configured FastAPI `onboard` endpoint to accept PDF file uploads.
  - Integrated **PyMuPDF** (`fitz`) to extract raw text page-by-page.
  - Setup the **Resume Extraction Agent** (via LLM) to produce structured profile JSONs (languages, tools, experience, projects, education).
  - Chunked parsed profiles into 5 semantic sections (`Education`, `Projects`, `Skills`, `Experience`, `Career Goals`) and stored them under the user's vector index.

---

## 🛡️ 4. API Robustness & Fallback Resilience

- **LLM JSON Repair Helper** ([llm_service.py](file:///home/satyansh/communeos/backend/services/llm_service.py)):
  - Implemented `repair_json(s)` to reconstruct truncated JSON responses. If free-tier APIs cutoff early, it closes open quotes and appends missing brackets/braces to prevent JSON decode failures.
- **Intelligent Local Fallback Scanner** ([resume_service.py](file:///home/satyansh/communeos/backend/services/resume_service.py)):
  - Replaced the hardcoded `["Python", "Linux"]` mock profile fallback with a case-insensitive keyword scanner. If the LLM is rate-limited or offline, the backend scans the raw PDF text for 30+ developer keywords and sets those as their profile skills instead of returning generic mocks.

---

## 🤖 5. Agent Pipelines & Orchestrator Personalization

- **Memory Agent** ([memory_agent.py](file:///home/satyansh/communeos/backend/agents/memory_agent.py)):
  - Created a dedicated agent to query the user's vector database and community memory catalog, merging results into a unified RAG context block.
- **Personalized Agent Routings**:
  - Rewrote the **Orchestrator** ([orchestrator.py](file:///home/satyansh/communeos/backend/services/orchestrator.py)) to fetch RAG context via the Memory Agent and inject it into the reasoning prompts.
  - Updated **Identity Agent** ([identity_agent.py](file:///home/satyansh/communeos/backend/agents/identity_agent.py)), **Discovery Agent** ([discovery_agent.py](file:///home/satyansh/communeos/backend/agents/discovery_agent.py)), **Learning Agent** ([learning_agent.py](file:///home/satyansh/communeos/backend/agents/learning_agent.py)), and **Mentor Agent** ([mentor_agent.py](file:///home/satyansh/communeos/backend/agents/mentor_agent.py)) to reason dynamically over the user's uploaded resume and matched community catalog resources.
- **Test Suite Updates**:
  - Modified [test_agents.py](file:///home/satyansh/communeos/backend/tests/test_agents.py) to patch the `LLMService` class methods directly (using `patch.object`) rather than unstable string paths, bypassing package attribute conflicts.
  - Refactored [test_llm_service.py](file:///home/satyansh/communeos/backend/tests/test_llm_service.py) to correctly mock settings and fallback assertions.

---

## 🎨 6. Frontend Onboarding & Dashboard UI Updates

- **Git Conflict Resolution** ([page.tsx](file:///home/satyansh/communeos/frontend/app/page.tsx)):
  - Merged local branch console states and upstream onboarding lifecycles.
- **Expanded Onboarding Form**:
  - Created input fields for **Name**, **Current Role**, **Skill Level** (Beginner, Intermediate, Advanced, Expert select dropdown), **Interests**, **Career Goal**, **Short Bio**, and a **PDF Resume File Upload**.
  - Packaged inputs into a `FormData` object and submitted it directly to the `/onboard` endpoint.
- **Responsive Layout Adjustments**:
  - Exposed user navbar card and Logout button on all viewport sizes (removed `hidden md:flex` constraints).
  - Embedded an **"Edit Profile & Resume"** CTA button inside the main Welcome Card, giving users instant access to re-onboarding and PDF re-uploads.
