"""
CommuneOS Identity Agent
Analyzes user profile, resume, GitHub, and portfolio to detect structured skills and preferences.
"""
import json
from typing import Any, Dict, Optional
from agents.base_agent import BaseAgent
from config import settings
from services.llm_service import llm_service
from utils.logger import get_logger

logger = get_logger("agent.identity")


class IdentityAgent(BaseAgent):
    """
    Agent 1: Identity / Profile Analysis
    
    Detects user skills, learning preferences, and career goals
    by analyzing their profile, uploaded resume, and GitHub data.
    """
    name = "identity_agent"
    cache_ttl = 3600  # 1 hour

    async def run_stateless(self, user_id: str) -> Dict[str, Any]:
        """
        Stateless execution of the Identity Agent.
        Reads all inputs directly from the database, runs LLM analysis,
        and saves the structured output in identities_table.
        """
        from services.db import users_table, resumes_table, identities_table, community_members_table, communities_table
        
        # 1. Fetch member profile
        profile = users_table.get(user_id.lower(), {})
        if not profile:
            logger.warning(f"Profile for user '{user_id}' not found in database. Using empty defaults.")
            profile = {}
            
        # 2. Fetch parsed resume
        resume = resumes_table.get(user_id.lower(), {})
        
        # 3. Fetch github data
        github_username = profile.get("github_username")
        github_data = {}
        if github_username:
            from services.github_service import get_github_profile_data
            try:
                github_data = await get_github_profile_data(github_username)
            except Exception as e:
                logger.error(f"Failed to fetch GitHub data for {github_username}: {e}")
            
        # 4. Community context
        member_info = community_members_table.get(user_id.lower())
        community_id = member_info["community_id"] if member_info else "comm-gpu"
        community_desc = ""
        community_name = ""
        if community_id:
            comm = communities_table.get(community_id.lower())
            if comm:
                community_name = comm.get("name", "")
                community_desc = comm.get("description", "")
                
        community_context = f"Community: {community_name}. Description: {community_desc}"
        
        # 5. Build prompt
        skills_summary = ", ".join([f"{k} (level {v}/5)" for k, v in profile.get("skills", {}).items()]) if profile.get("skills") else "None"
        resume_summary = f"Skills: {', '.join(resume.get('skills', []))}. Technologies: {', '.join(resume.get('technologies', []))}. Frameworks: {', '.join(resume.get('frameworks', []))}." if resume else "No resume uploaded."
        
        gh_langs = github_data.get("languages", []) if github_data else []
        gh_topics = github_data.get("topics", []) if github_data else []
        github_summary = f"Languages: {', '.join(gh_langs)}. Topics: {', '.join(gh_topics)}." if github_data else "No github connected."
        
        prompt = f"""Analyze the community member's information and build a structured identity profile.
        
User: {profile.get('username', 'Unknown')}
Bio: {profile.get('bio', '')}
Experience Level: {profile.get('experience_level', '')}
Portfolio URL: {profile.get('portfolio_url', '')}
Stated Interests: {', '.join(profile.get('interests', []))}
Career Goals: {', '.join(profile.get('career_goals', []))}
Preferred Technologies: {', '.join(profile.get('preferred_technologies', []))}
Preferred Domains: {', '.join(profile.get('preferred_domains', []))}
Learning Preferences: {', '.join(profile.get('learning_preferences', []))}
Stated Skills: {skills_summary}

Resume Information:
{resume_summary}

GitHub Data:
{github_summary}

Community Context:
{community_context}

Based on all the provided coordinates, return a structured identity analysis."""

        system_prompt = """You are the Identity Agent for CommuneOS.
Your job is to analyze a community member's coordinates and produce a structured identity profile.
You MUST return ONLY valid JSON in this exact structure:
{
  "skill_level": "Beginner|Intermediate|Advanced|Expert",
  "skills": ["Skill1", "Skill2"],
  "technologies": ["Tech1", "Tech2"],
  "interests": ["Interest1", "Interest2"],
  "domains": ["Domain1", "Domain2"],
  "goals": ["Goal1", "Goal2"],
  "confidence_score": 0.0-1.0
}

Rules:
- skill_level must be one of: Beginner, Intermediate, Advanced, Expert
- skills, technologies, interests, domains, goals must be flat lists of strings.
- confidence_score must be a float between 0.0 and 1.0.
- Do NOT include any markdown code blocks, paragraphs, explanations, or text outside the JSON object.
"""

        result_json, is_fallback = await llm_service.complete_json(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.2
        )
        
        if is_fallback or not result_json:
            logger.warning(f"LLM run failed for user {user_id}. Using deterministic fallback.")
            result_json = {
                "skill_level": profile.get("experience_level") or "Intermediate",
                "skills": list(profile.get("skills", {}).keys()) or ["Python"],
                "technologies": profile.get("preferred_technologies") or ["Git"],
                "interests": profile.get("interests") or ["Machine Learning"],
                "domains": profile.get("preferred_domains") or ["AI Systems"],
                "goals": profile.get("career_goals") or ["Learn CUDA"],
                "confidence_score": 0.7
            }
            is_fallback = True
            
        # Map Sprint 1 keys to Sprint 2 keys if needed (for backwards compatibility/testing)
        if "detected_skills" in result_json and "skills" not in result_json:
            result_json["skills"] = [s["name"] for s in result_json["detected_skills"]]
            if not result_json.get("skill_level") and result_json["detected_skills"]:
                result_json["skill_level"] = result_json["detected_skills"][0].get("proficiency", "Intermediate")
        if "expertise_areas" in result_json and "domains" not in result_json:
            result_json["domains"] = result_json["expertise_areas"]
        if "growth_areas" in result_json and "goals" not in result_json:
            result_json["goals"] = result_json["growth_areas"]
        if "overall_confidence" in result_json and "confidence_score" not in result_json:
            result_json["confidence_score"] = result_json["overall_confidence"]

        # Map Sprint 2 keys to Sprint 1 keys (so other agents and tests don't break)
        if "skills" in result_json and "detected_skills" not in result_json:
            result_json["detected_skills"] = [
                {"name": s, "proficiency": result_json.get("skill_level", "Intermediate"), "confidence": result_json.get("confidence_score", 0.8), "source": "stated"}
                for s in result_json.get("skills", [])
            ]
        if "domains" in result_json and "expertise_areas" not in result_json:
            result_json["expertise_areas"] = result_json["domains"]
        if "goals" in result_json and "growth_areas" not in result_json:
            result_json["growth_areas"] = result_json["goals"]
        if "confidence_score" in result_json and "overall_confidence" not in result_json:
            result_json["overall_confidence"] = result_json["confidence_score"]
        if "summary" not in result_json:
            result_json["summary"] = f"Profile built by Identity Agent. Skill level: {result_json.get('skill_level')}"
        if "learning_preference" not in result_json:
            result_json["learning_preference"] = profile.get("learning_style") or "visual"
            
        # Ensure user_id and is_fallback are in the result
        result_json["user_id"] = user_id
        result_json["_is_fallback"] = is_fallback
        
        # Save to database
        identities_table[user_id.lower()] = result_json
        
        return result_json

    async def _process(self, user_id: str, user_data: Dict, *args, **kwargs) -> Dict[str, Any]:
        """Core processing logic — delegating to stateless database run."""
        res = await self.run_stateless(user_id)
        
        # Copy to avoid mutating DB reference directly
        res_copy = dict(res)
        
        # Ensure compatibility fields are present
        if "detected_skills" not in res_copy:
            res_copy["detected_skills"] = [
                {"name": s, "proficiency": res_copy.get("skill_level", "Intermediate"), "confidence": res_copy.get("confidence_score", 0.8), "source": "stated"}
                for s in res_copy.get("skills", [])
            ]
        if "expertise_areas" not in res_copy:
            res_copy["expertise_areas"] = res_copy.get("domains", [])
        if "growth_areas" not in res_copy:
            res_copy["growth_areas"] = res_copy.get("goals", [])
        if "learning_preference" not in res_copy:
            res_copy["learning_preference"] = user_data.get("learning_style") or "visual"
        if "overall_confidence" not in res_copy:
            res_copy["overall_confidence"] = res_copy.get("confidence_score", 0.8)
        if "summary" not in res_copy:
            res_copy["summary"] = f"Profile built by Identity Agent. Skill level: {res_copy.get('skill_level')}"
            
        return res_copy

    def _get_fallback(self, user_id: str, user_data: Dict, *args, **kwargs) -> Dict[str, Any]:
        # Return fallback database structure
        res = {
            "user_id": user_id,
            "skill_level": "Intermediate",
            "skills": ["Python", "Machine Learning"],
            "technologies": ["Git", "Docker"],
            "interests": ["GPU Architectures"],
            "domains": ["AI Systems"],
            "goals": ["Optimize matrix multiplication"],
            "confidence_score": 0.65,
            
            # Sprint 1
            "detected_skills": [
                {"name": "Python", "proficiency": "Intermediate", "confidence": 0.8, "source": "stated"},
                {"name": "Machine Learning", "proficiency": "Beginner", "confidence": 0.6, "source": "inferred"}
            ],
            "expertise_areas": ["Systems Programming"],
            "growth_areas": ["Distributed Systems"],
            "learning_preference": "visual",
            "overall_confidence": 0.65,
            "summary": "Fallback profile data"
        }
        return res
