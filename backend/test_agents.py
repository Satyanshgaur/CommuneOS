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
        # Retrieve or create a clean asyncio event loop for running agent reasoners
        try:
            self.loop = asyncio.get_event_loop()
        except RuntimeError:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

    def test_rahul_member_pipeline(self):
        """Test that the sequential agent pipeline successfully processes Rahul's profile and returns valid structures."""
        async def run_pipeline():
            # 1. Identity Agent checks
            profile = await run_identity_agent("rahul")
            self.assertEqual(profile.skill_level, "Intermediate/Advanced")
            self.assertIn("CUDA", profile.interests)
            self.assertTrue(profile.reasoning.startswith("Identity Agent:"))

            # 2. Discovery Agent checks
            discovery = await run_discovery_agent("rahul", profile)
            self.assertIn("gpu-computing", discovery.recommended_communities)
            self.assertIn("cuda-optimization", discovery.recommended_resources)
            self.assertIn("gpu-ama", discovery.recommended_events)

            # 3. Learning Agent checks
            learning = await run_learning_agent("rahul", profile)
            self.assertEqual(len(learning.priorities), 3)
            self.assertIn("Attend GPU Workshop with Sarah", learning.priorities)

            # 4. Mentor Agent checks
            mentor = await run_mentor_agent("rahul", profile)
            self.assertEqual(mentor.mentor_name, "Sarah")
            self.assertEqual(mentor.mentor_role, "Senior CUDA Engineer @ Nvidia")

            # 5. Full Dashboard aggregation check
            dashboard = await get_member_dashboard("rahul")
            self.assertEqual(dashboard["name"], "Rahul")
            self.assertEqual(dashboard["recommended_mentor"]["name"], "Sarah")
            self.assertEqual(len(dashboard["priorities"]), 3)

        self.loop.run_until_complete(run_pipeline())

    def test_priya_member_pipeline(self):
        """Test that the sequential agent pipeline successfully processes Priya's profile and returns beginner recommendations."""
        async def run_pipeline():
            # 1. Identity Agent checks
            profile = await run_identity_agent("priya")
            self.assertEqual(profile.skill_level, "Beginner")
            self.assertIn("PyTorch", profile.interests)

            # 2. Discovery Agent checks
            discovery = await run_discovery_agent("priya", profile)
            self.assertIn("pytorch-study-group", discovery.recommended_communities)
            self.assertIn("intro-pytorch", discovery.recommended_resources)

            # 3. Learning Agent checks
            learning = await run_learning_agent("priya", profile)
            self.assertIn("Post your introduction in #introductions", learning.priorities)

            # 4. Mentor Agent checks
            mentor = await run_mentor_agent("priya", profile)
            self.assertEqual(mentor.mentor_name, "Elena")
            self.assertEqual(mentor.mentor_role, "Machine Learning Researcher")

            # 5. Full Dashboard aggregation check
            dashboard = await get_member_dashboard("priya")
            self.assertEqual(dashboard["name"], "Priya")
            self.assertEqual(dashboard["recommended_mentor"]["name"], "Elena")

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
            self.assertEqual(len(dashboard["health_summary"]["ignored_newcomers"]), 1)
            self.assertEqual(dashboard["health_summary"]["ignored_newcomers"][0], "Priya")

        self.loop.run_until_complete(run_loop())

if __name__ == '__main__':
    unittest.main()
