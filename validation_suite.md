# CommunityOS Agent Validation Suite

This document describes the validation suite designed to test the execution integrity, schema alignment, and output structures of the CommunityOS multi-agent orchestrator.

---

## 🚀 Execution Efficiency & Strategy

To ensure **high efficiency** and **offline resilience**, the test suite uses a mock-override isolation pattern:
1. **API Key Isolation:** The tests temporarily clear the `OPENROUTER_API_KEY` from `os.environ` during runtime.
2. **Local Path Fallback:** This forces `agentfield` reasoners to skip OpenRouter LLM roundtrips and resolve instantly using high-fidelity local mock data structures.
3. **Sub-millisecond Performance:** The entire test suite validates the complex Member and Organizer loops in **less than 230 milliseconds**.

---

## 📝 The Test Suite: `backend/test_agents.py`

The test suite is written using the standard Python `unittest` library and tests the sequential execution path and JSON outputs.

Here is the implementation:

```python
# backend/test_agents.py

import unittest
import asyncio
import os
from backend.agents import (
    run_identity_agent,
    run_discovery_agent,
    run_learning_agent,
    run_mentor_agent,
    run_health_agent,
    run_organizer_agent,
    get_member_dashboard,
    get_organizer_dashboard
)

class TestCommunityOSAgents(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Force local execution mode during tests to keep them offline and sub-millisecond fast
        cls.original_key = os.environ.get("OPENROUTER_API_KEY")
        if "OPENROUTER_API_KEY" in os.environ:
            del os.environ["OPENROUTER_API_KEY"]

    @classmethod
    def tearDownClass(cls):
        # Restore API key if it was present
        if cls.original_key:
            os.environ["OPENROUTER_API_KEY"] = cls.original_key

    def setUp(self):
        try:
            self.loop = asyncio.get_event_loop()
        except RuntimeError:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

    def test_rahul_member_pipeline(self):
        """Test that the sequential agent pipeline successfully processes Rahul's profile."""
        async def run_pipeline():
            # 1. Identity Agent (Skill profiling)
            profile = await run_identity_agent("rahul")
            self.assertEqual(profile.skill_level, "Intermediate/Advanced")
            self.assertIn("CUDA", profile.interests)

            # 2. Discovery Agent (Content matching)
            discovery = await run_discovery_agent("rahul", profile)
            self.assertIn("gpu-computing", discovery.recommended_communities)
            self.assertIn("cuda-optimization", discovery.recommended_resources)

            # 3. Learning Agent (Checklist roadmaps)
            learning = await run_learning_agent("rahul", profile)
            self.assertEqual(len(learning.priorities), 3)

            # 4. Mentor Agent (Expert matching)
            mentor = await run_mentor_agent("rahul", profile)
            self.assertEqual(mentor.mentor_name, "Sarah")

            # 5. Full Dashboard aggregation
            dashboard = await get_member_dashboard("rahul")
            self.assertEqual(dashboard["name"], "Rahul")
            self.assertEqual(dashboard["recommended_mentor"]["name"], "Sarah")

        self.loop.run_until_complete(run_pipeline())

    def test_priya_member_pipeline(self):
        """Test that the sequential agent pipeline successfully processes Priya's profile."""
        async def run_pipeline():
            # 1. Identity Agent
            profile = await run_identity_agent("priya")
            self.assertEqual(profile.skill_level, "Beginner")

            # 2. Discovery Agent
            discovery = await run_discovery_agent("priya", profile)
            self.assertIn("pytorch-study-group", discovery.recommended_communities)

            # 3. Learning Agent
            learning = await run_learning_agent("priya", profile)
            self.assertIn("Post your introduction in #introductions", learning.priorities)

            # 4. Mentor Agent
            mentor = await run_mentor_agent("priya", profile)
            self.assertEqual(mentor.mentor_name, "Elena")

        self.loop.run_until_complete(run_pipeline())

    def test_organizer_operations_loop(self):
        """Test that the Community Health and Organizer agents parse metrics and flag active risks."""
        async def run_loop():
            # 1. Health Agent checks
            health = await run_health_agent()
            self.assertIn("Priya", health.ignored_newcomers)
            self.assertIn("Vikram (Inactive for 21 days)", health.inactive_members)

            # 2. Organizer Agent checks
            insights = await run_organizer_agent(health)
            self.assertTrue(len(insights.suggested_actions) > 0)
            self.assertEqual(insights.suggested_actions[0].action, "Reply to Priya's introduction in #introductions and introduce her to Elena.")

            # 3. Full Organizer Dashboard check
            dashboard = await get_organizer_dashboard()
            self.assertEqual(dashboard["metrics"]["active_members_ratio"], "83%")

        self.loop.run_until_complete(run_loop())
