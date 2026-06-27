import httpx, json

print("--- Testing all endpoints ---")
base = "http://localhost:8000"

# Health
r = httpx.get(base + "/health")
print("GET /health:", r.status_code)

# User
r = httpx.get(base + "/api/v1/users/rahul")
print("GET /users/rahul:", r.status_code)

# Community metrics
r = httpx.get(base + "/api/v1/community/metrics")
d = r.json()["data"]
print("GET /community/metrics:", r.status_code, "| score=", d["community_health_score"])

# Discovery channels
r = httpx.get(base + "/api/v1/discovery/rahul/channels")
d = r.json()["data"]
print("GET /discovery/rahul/channels:", r.status_code, "| count=", d["count"])

# Learning roadmap
r = httpx.get(base + "/api/v1/learning/rahul/roadmap")
print("GET /learning/rahul/roadmap:", r.status_code)

# Organizer actions
r = httpx.get(base + "/api/v1/organizer/actions")
d = r.json()["data"]
print("GET /organizer/actions:", r.status_code, "| count=", d["count"])

# Personalize pipeline - with 90s timeout
print("POST /agents/personalize/rahul (calling LLM - up to 90s)...")
r = httpx.post(base + "/api/v1/agents/personalize/rahul", timeout=90)
print("POST /agents/personalize/rahul:", r.status_code)
if r.status_code == 200:
    d = r.json()["data"]
    print("  pipeline_ms=", d.get("pipeline_time_ms"), "fallback=", d.get("fallback_used"))
    print("  identity skills=", len(d.get("identity", {}).get("detected_skills", [])))
    print("  channels=", len(d.get("discovery", {}).get("recommended_channels", [])))
    print("  milestones=", len(d.get("learning", {}).get("milestones", [])))
    mentor = d.get("mentor", {}).get("primary_mentor") or {}
    print("  mentor=", mentor.get("name", "none"))
    print("ALL GOOD - Phase 1 pipeline working!")
else:
    print("ERROR:", r.text[:400])
