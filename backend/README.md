# CommuneOS Agentic Backend

CommuneOS is a high-performance agentic backend powered by **FastAPI** and **Python 3.14+**. It coordinates a team of 6 cooperative AI agents to dynamically personalize community environments, detect churn risks, and automate operational actions.

---

## 🚀 Key Features

* **6 Specialized AI Agents**:
  1. **Identity Agent**: Analyzes biography, goals, and chat context to detect skills, proficiency levels, and learning preferences.
  2. **Discovery Agent**: Matches members with relevant channels and resources based on identity profiles.
  3. **Learning Agent**: Generates structured, week-by-week learning roadmaps and daily checklists.
  4. **Mentor Agent**: Evaluates timezone availability, teaching style, and expertise alignment to recommend the best expert mentors.
  5. **Health Agent**: Monitors community-level activity to spot inactive members, content gaps, and sentiment trends.
  6. **Organizer Agent**: Converts health metrics into prioritized action items and workshop suggestions for community managers.
* **Centralized Orchestrator**: Coordinates sequential and parallel execution paths for user personalization and community health analysis.
* **Instant Fallback Recovery**: Automatically switches to local seed-based mock profiles if LLM calls fail, time out, or exceed rate limits.
* **Double LLM Fallback**: Immediately switches to a secondary fallback model (e.g. Llama 3) if the primary model (Gemma 4) suffers a service outage (502/503/504) or timeout.
* **In-Memory TTL Caching**: Caches prompt hashes and final agent outputs to reduce OpenRouter API costs and keep response latencies under 10ms on cache hits.
* **Performance Analytics**: Tracks P50/P95/P99 latencies, cache hit ratios, and fallback rates.

---

## 📂 Project Structure

```
backend/
├── main.py                     # FastAPI application entry point & CORS setup
├── config.py                   # Pydantic Settings configuration (loads .env)
├── .env                        # Configuration environment variables
├── requirements.txt            # Project dependencies
├── agents/                     # The 6 AI Agents
│   ├── base_agent.py           # Abstract Base class with cache/timing/analytics
│   ├── identity_agent.py
│   ├── discovery_agent.py
│   ├── learning_agent.py
│   ├── mentor_agent.py
│   ├── health_agent.py
│   └── organizer_agent.py
├── models/                     # Pydantic schemas (User, Agent Output, Metrics)
│   ├── user.py
│   ├── agent_response.py
│   └── community.py
├── services/                   # Business logic layer
│   ├── llm_service.py          # OpenRouter wrapper (retries, timeouts, fallback)
│   ├── cache_service.py        # TTL-based caching service
│   ├── mock_data.py            # Expanded seed-based mock database (10 mentors, 17 resources)
│   ├── analytics.py            # In-memory execution latency monitors
│   └── orchestrator.py         # Sequential & parallel pipeline managers
├── api/v1/endpoints/           # REST endpoints
│   ├── agents.py               # Orchestrator & status routes
│   ├── users.py                # User CRUD routes
│   ├── community.py            # Metrics, channels, and roadmaps
│   └── health.py               # System & LLM status endpoints
└── tests/                      # Pytest suite
    ├── test_phase1.py          # Core structure & models unit tests
    ├── test_agents.py          # Per-agent mock LLM & fallback tests
    ├── test_llm_service.py     # Retry & model fallback mechanics tests
    └── verify_api.py           # End-to-end API integration script
```

---

## 🛠️ Configuration Settings

The server loads its settings from the `.env` file in the `backend/` directory:

| Environment Variable | Default Value | Description |
| :--- | :--- | :--- |
| `OPENROUTER_API_KEY` | *(None)* | OpenRouter API Key for LLM access. |
| `OPENROUTER_MODEL` | `google/gemma-4-31b-it:free` | Primary LLM model for agent calls. |
| `OPENROUTER_FALLBACK_MODEL` | `meta-llama/llama-3-8b-instruct:free` | Fallback model if primary fails. |
| `HOST` | `0.0.0.0` | Bind host address. |
| `PORT` | `8000` | Bind port number. |
| `LLM_TIMEOUT_SECONDS` | `10` | Hard timeout cap for a single LLM API call. |
| `AGENT_MAX_RETRIES` | `0` | Retries for transient LLM errors. |
| `CACHE_TTL_AGENT` | `3600` | Caching duration (seconds) for agent results. |
| `CACHE_TTL_LLM` | `86400` | Caching duration (seconds) for prompt outputs. |

---

## 📡 REST API Reference

All routes are prefixed with `/api/v1` (except system status routes).

### Agent Pipelines
* `POST /api/v1/agents/personalize/{user_id}`: Runs the full personalization pipeline (Identity → Discovery + Learning → Mentor). Uses cached values if present. Falls back to mock data if LLM times out (>45s).
* `GET /api/v1/agents/status/{user_id}`: Check the progress status of a running personalization pipeline.
* `POST /api/v1/agents/refresh/{user_id}`: Invalidates agent caches for the user and forces a fresh LLM run.
* `POST /api/v1/agents/community/health`: Runs the community health monitoring pipeline (Health Agent → Organizer Agent).

### User Management
* `POST /api/v1/users/create`: Creates a new user profile using basic JSON info (username, bio, interests, goals).
* `GET /api/v1/users/{user_id}`: Retrieves the user's basic profile details.
* `PUT /api/v1/users/{user_id}`: Updates user details and invalidates corresponding agent caches.
* `GET /api/v1/users/{user_id}/profile`: Gets the complete cached personalization profile for a user.

### System Diagnostics
* `GET /health`: Basic backend check. Returns `status: "healthy"`.
* `GET /health/llm`: Tests connection to OpenRouter. Returns availability status and configured models.
* `GET /metrics/performance`: Returns P50/P95/P99 latency values, cache hits/misses, and agent success rates.

---

## 🧪 Running Tests

A complete suite of unit and integration tests is located in the `tests/` folder.

To install test dependencies:
```bash
python -m pip install pytest pytest-asyncio
```

To run all unit tests:
```bash
python -m pytest tests/
```

To run end-to-end API integration verification (requires the server to be running on port 8000):
```bash
python tests/verify_api.py
```

---

## 🏃 Run the Application

Start the FastAPI application using `uvicorn`:

```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API docs will then be available on:
* **Interactive Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
* **ReDoc manual**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
