# backend/main.py

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load env variables from .env if present
load_dotenv()

from backend.agents import get_member_dashboard, get_organizer_dashboard

app = FastAPI(
    title="CommunityOS API",
    description="Backend services powered by AgentField and OpenRouter for adaptive AI community platform insights.",
    version="1.0.0"
)

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to CommunityOS API backend. Running successfully!"}

@app.get("/api/members/{member_id}")
async def get_member(member_id: str):
    member_id = member_id.lower().strip()
    if member_id not in ["rahul", "priya"]:
        raise HTTPException(status_code=404, detail="Member persona not found. Select 'rahul' or 'priya'.")
    try:
        data = await get_member_dashboard(member_id)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent runtime error: {str(e)}")

@app.get("/api/organizer")
async def get_organizer():
    try:
        data = await get_organizer_dashboard()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent runtime error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    # Allow running directly via python -m backend.main
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
