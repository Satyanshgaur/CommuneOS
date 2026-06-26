> This document acts as the persistent architectural roadmap for CommunityOS as it transitions from a synchronous pipeline prototype into a production event-driven SaaS application.

---

## Vision
CommunityOS is an AI-native operating system for online communities. Instead of acting as a chatbot, it continuously understands members, recommends learning resources, matches mentors, monitors community health, and assists organizers.

The current prototype proves the agent orchestration pipeline. The next goal is transforming it into a production SaaS platform.

---

## Core Architectural Blueprint

The high-level architecture separates the frontend presentation layer, backend orchestration, event scheduling, and pgvector storage.

```mermaid
graph TD
    subgraph Client ["Client Layer"]
        NextJS["Next.js Frontend (TypeScript & Tailwind)"]
    end

subgraph Auth ["Auth Layer"]
        SupabaseAuth["Supabase Auth"]
    end

    subgraph API ["API & Scheduling Layer"]
        FastAPI["FastAPI App Server"]
        EventBus["Redis Event Bus / Celery Workers"]
    end

    subgraph Agents ["Stateless AI Reasoning Layer"]
        IA["Identity Agent (Profile Analyzer)"]
        DA["Discovery Agent (Matchmaking Engine)"]
        LA["Learning Agent (Roadmap Builder)"]
        MA["Mentor Agent (Expert Matcher)"]
        HA["Health Agent (Churn Monitor)"]
        OA["Organizer Agent (Actions & Insight Panel)"]
    end

    subgraph Database ["Storage Layer"]
        Postgres["Supabase PostgreSQL (Primary DB)"]
        VectorDB["pgvector (Semantic Search)"]
        Storage["Supabase Storage (Resumes, PDFs)"]
    end

    NextJS -->|Auth Requests| SupabaseAuth
    NextJS -->|REST API Calls| FastAPI
    FastAPI -->|Publish Event| EventBus
    EventBus -->|Trigger Agent| IA
    EventBus -->|Trigger Agent| DA
    EventBus -->|Trigger Agent| LA
    EventBus -->|Trigger Agent| MA
    EventBus -->|Trigger Agent| HA
    EventBus -->|Trigger Agent| OA

    IA & DA & LA & MA & HA & OA -->|Read/Write Structured Data| Postgres
    MA -->|Query Embeddings| VectorDB
    IA -->|Access Resumes| Storage
```

---

## Guiding Architectural Principles

### 1. Event-Driven Architecture
The platform will transition from request-driven to event-driven execution. Instead of blocking web requests to wait for LLMs, the system publishes events to a Redis-backed queue.

```
[User Uploads Resume]
         ↓ (Publish Event: "resume.uploaded")
[Queue: Celery/Redis]
         ↓ (Trigger Worker)
[Identity Agent runs & Updates User DB]
         ↓ (Publish Event: "identity.updated")
[Discovery Agent runs & Updates Recommendations]
         ↓ (Publish Event: "discovery.updated")
[Learning Agent runs & Refreshes Roadmap]
         ↓
[Dashboard Updates via Supabase Realtime]
```
> [!TIP]
> This pattern allows the UI to update asynchronously using Supabase Realtime, making the community feel "alive" as agents react to user activity in the background.

### 2. Stateless AI Agents
Agents remain completely stateless. They accept all necessary user data, current context, and historical interactions as prompt inputs, returning only structured profiles.
- **Why?** Stateless agents are easy to test, cache, scale horizontally, and allow models to be upgraded easily without refactoring state stores.

### 3. Database as Source of Truth
The database (Supabase PostgreSQL)—not the AI model context—holds the system's long-term memory.
- All relationships, history, achievements, and roadmap completions are structured as table columns.

### 4. Structured AI Outputs
Agents return structured JSON objects matching Pydantic schemas. They do not return free-form paragraphs.
- **Why?** This ensures recommendations, learning steps, and actions are searchable, editable, versionable, and directly parsable by downstream systems.

### 5. AI Never Owns Business Logic
AI performs reasoning, but business logic is deterministic.
- *Example:* Instead of allowing an LLM to freely decide a mentor, the server uses a mathematical **Vector Similarity Search** (via `pgvector`) to find the top 5 matches, and the LLM simply reviews and writes the natural language explanation for why those matches align.

---

## Phase-by-Phase Execution Plan

### Phase 1 — Authentication & Multi-Tenant Communities
* **Goal:** Upgrade CommunityOS into a multi-tenant SaaS platform.
* **Database Tables:** `users`, `communities`, `community_members`, `roles`.
* **Roles:** `Owner`, `Admin`, `Moderator`, `Mentor`, `Member`.
* **Tenant Isolation:** Every record belongs to a specific `community_id`, with Row-Level Security (RLS) policies enforcing isolation.

### Phase 2 — Member Onboarding Pipeline
* **Goal:** Automatically build user-interest skill profiles on day one.
* **Onboarding Inputs:** Resume PDFs, GitHub usernames, portfolios, interest tags.
* **Processing:** **Identity Agent** analyzes raw inputs and updates the member's Profile Graph.
* **Outputs:** Skills list, experience level, career domains, technical goals, and skill classifications.

### Phase 3 — Community Knowledge Layer
* **Goal:** Build the primary data layer that maps out community assets.
* **Data Entities:** Learning tracks, upcoming events, repositories, reading links, and verified mentors.
* **Agent Integration:** All downstream agents search this structured database instead of hallucinating options.

### Phase 4 — Discovery Agent
* **Goal:** Generate highly personalized matchmaking recommendations.
* **Logic:** Evaluates the user's `Identity Profile` and pairs it with the `Knowledge Layer`.
* **Outputs:** Channels to join, specific study groups, relevant events, active projects, and recommended articles.

### Phase 5 — Learning Agent
* **Goal:** Create actionable study guides.
* **Logic:** Maps the user's current skill level to their desired milestone.
* **Outputs:** Structured roadmap with checklists, deadlines, hands-on tasks, and recommended reading. Users mark items complete in the UI.

### Phase 6 — Semantic Mentor Matching
* **Goal:** Dynamic, automated mentor matching.
* **Logic:** Generates embeddings of member profiles and runs a cosine-similarity search against mentor specialties in PostgreSQL.
* **Filtering:** Removes unavailable mentors, and routes the top candidates to the **Mentor Agent** for final explanatory ranking.

### Phase 7 — Organizer Intelligence
* **Goal:** Build the mission control dashboard for community managers.
* **Metrics:** Churn risk, inactive members, neglected newcomers, unanswered discussion threads, and mentor loads.
* **Action Engine:** Proposes operational task suggestions (e.g., *"Connect Priya with Elena"*).

### Phase 8 — Continuous Community Health
* **Goal:** Run diagnostics automatically as a background daemon.
* **Logic:** Every 6 hours, the **Health Agent** scans recent message telemetry and flags drop-offs.
* **Outputs:** Dispatches Slack/Discord alerts or pushes tasks directly to the organizer's active dashboard backlog.

### Phase 9 — Document Intelligence (RAG)
* **Goal:** Support arbitrary community guides, documentation, and policy uploads.
* **Logic:** Text chunking, embedding generation using OpenAI/Ollama, storage in `pgvector`, and Retrieval-Augmented Generation (RAG) for agents answering community questions.

### Phase 10 — Community Memory
* **Goal:** Build long-term memory for personalization.
* **Logic:** Tracks historical search queries, views, project participation, and chat activities.
* **Outputs:** Future recommendations automatically adjust based on past user behaviors.

### Phase 11 — Event Bus Integration
* **Goal:** Transition backend communication to Celery and Redis.
* **Implementation:** FastAPI publishes event payloads. Background workers subscribe and execute tasks asynchronously.
* **Sample Events:** `member.joined`, `resume.uploaded`, `roadmap.updated`, `event.completed`.

### Phase 12 — AI Automations
* **Goal:** Enable user-configurable automated jobs.
* **Examples:** Custom weekly learning digests, inactive member alerts for admins, check-in reminders for mentors.

### Phase 13 — Community Analytics
* **Goal:** Deep metrics reporting for organizers.
* **Visuals:** Growth curves, skill distribution maps, learning path completion funnels, and retention charts.

### Phase 14 — Integrations
* **Goal:** Connect live community pipelines.
* **Integrations:** GitHub (commit/issue events), Discord/Slack (active chat metrics), Google Calendar (event sync), Notion (knowledge syncing).

---

## Recommended Technology Stack

| Layer | Technology | Details |
|---|---|---|
| **Frontend** | Next.js, TypeScript, TailwindCSS, shadcn/ui | Fast, lightweight rendering with rich parchment design system. |
| **State Management** | React Query, Zustand | Handles client-side API caching and real-time interface sync. |
| **Backend** | FastAPI, Pydantic, SQLAlchemy | Asynchronous API handling, strict validation, and ORM layer. |
| **Queue / Cache** | Celery, Redis | Manages the background agent event bus and API cache. |
| **Database** | Supabase (PostgreSQL) | Primary data store with row-level security, auth, and realtime. |
| **Vector Engine** | pgvector (PostgreSQL) | Multi-dimensional cosine search for mentors and knowledge RAG. |
| **Storage** | Supabase Storage | File storage for resumes, PDFs, and community documents. |
| **AI Orchestration** | AgentField, LiteLLM | Multi-agent definition, schema constraints, and LLM providers. |

