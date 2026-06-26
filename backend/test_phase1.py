# backend/test_phase1.py

import unittest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import Base, get_db
from backend.models import User, Community, CommunityMember
from backend.main import app

# Create test SQLite database
TEST_DATABASE_URL = "sqlite:///./test_communityos.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class TestPhase1Endpoints(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)

    @classmethod
    def tearDownClass(cls):
        Base.metadata.drop_all(bind=engine)
        import os
        if os.path.exists("./test_communityos.db"):
            try:
                os.remove("./test_communityos.db")
            except Exception:
                pass

    def setUp(self):
        # Override the get_db dependency
        def override_get_db():
            db = TestingSessionLocal()
            try:
                yield db
            finally:
                db.close()
        app.dependency_overrides[get_db] = override_get_db
        self.client = TestClient(app)

    def tearDown(self):
        # Clean up database sessions and tables between tests
        app.dependency_overrides.clear()
        db = TestingSessionLocal()
        for table in reversed(Base.metadata.sorted_tables):
            db.execute(table.delete())
        db.commit()
        db.close()

    def test_registration_and_login(self):
        # 1. Register a new user
        reg_payload = {
            "id": "testuser",
            "email": "test@example.com",
            "password": "mypassword123",
            "full_name": "Test User"
        }
        res_reg = self.client.post("/api/auth/register", json=reg_payload)
        self.assertEqual(res_reg.status_code, 201)
        data = res_reg.json()
        self.assertEqual(data["id"], "testuser")
        self.assertEqual(data["email"], "test@example.com")
        self.assertEqual(data["full_name"], "Test User")

        # 2. Try to register with duplicate ID
        res_dup = self.client.post("/api/auth/register", json=reg_payload)
        self.assertEqual(res_dup.status_code, 400)

        # 3. Login using JSON
        login_payload = {
            "id": "testuser",
            "password": "mypassword123"
        }
        res_login = self.client.post("/api/auth/login-json", json=login_payload)
        self.assertEqual(res_login.status_code, 200)
        token_data = res_login.json()
        self.assertIn("access_token", token_data)
        self.assertEqual(token_data["token_type"], "bearer")

        # 4. Login using standard OAuth2 Form
        form_payload = {
            "username": "testuser",
            "password": "mypassword123"
        }
        res_login_form = self.client.post("/api/auth/login", data=form_payload)
        self.assertEqual(res_login_form.status_code, 200)
        self.assertIn("access_token", res_login_form.json())

    def test_profile_retrieval_and_update(self):
        # Register and login first
        self.client.post("/api/auth/register", json={
            "id": "testprofile",
            "email": "profile@example.com",
            "password": "password123",
            "full_name": "Profile Owner"
        })
        res_login = self.client.post("/api/auth/login-json", json={
            "id": "testprofile",
            "password": "password123"
        })
        token = res_login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Retrieve profile
        res_me = self.client.get("/api/auth/me", headers=headers)
        self.assertEqual(res_me.status_code, 200)
        self.assertEqual(res_me.json()["full_name"], "Profile Owner")

        # Update profile
        update_payload = {
            "full_name": "New Full Name",
            "bio": "New Bio details",
            "skills": ["Rust", "PyTorch", "CUDA"],
            "skill_level": "Intermediate",
            "goals": "Build cool things"
        }
        res_update = self.client.put("/api/auth/me", json=update_payload, headers=headers)
        self.assertEqual(res_update.status_code, 200)
        updated_data = res_update.json()
        self.assertEqual(updated_data["full_name"], "New Full Name")
        self.assertEqual(updated_data["bio"], "New Bio details")
        self.assertEqual(updated_data["skills"], ["Rust", "PyTorch", "CUDA"])
        self.assertEqual(updated_data["skill_level"], "Intermediate")

    def test_multi_tenant_communities(self):
        # Register and login two separate users
        self.client.post("/api/auth/register", json={
            "id": "user1",
            "email": "user1@example.com",
            "password": "password123",
            "full_name": "User One"
        })
        self.client.post("/api/auth/register", json={
            "id": "user2",
            "email": "user2@example.com",
            "password": "password123",
            "full_name": "User Two"
        })

        res_login1 = self.client.post("/api/auth/login-json", json={"id": "user1", "password": "password123"})
        token1 = res_login1.json()["access_token"]
        headers1 = {"Authorization": f"Bearer {token1}"}

        res_login2 = self.client.post("/api/auth/login-json", json={"id": "user2", "password": "password123"})
        token2 = res_login2.json()["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}

        # 1. User 1 creates community
        comm_payload = {
            "id": "test-channel",
            "name": "Test Channel",
            "category": "Tech",
            "description": "Welcome to test channel"
        }
        res_create = self.client.post("/api/communities", json=comm_payload, headers=headers1)
        self.assertEqual(res_create.status_code, 200)
        self.assertEqual(res_create.json()["created_by"], "user1")

        # 2. List communities
        res_list = self.client.get("/api/communities")
        self.assertEqual(res_list.status_code, 200)
        self.assertEqual(len(res_list.json()), 1)
        self.assertEqual(res_list.json()[0]["name"], "Test Channel")

        # 3. User 2 joins community created by User 1
        res_join = self.client.post("/api/communities/test-channel/join", headers=headers2)
        self.assertEqual(res_join.status_code, 200)
        self.assertEqual(res_join.json()["user_id"], "user2")
        self.assertEqual(res_join.json()["role"], "Member")

        # 4. Check joined communities list for User 2
        res_my_comm = self.client.get("/api/communities/my", headers=headers2)
        self.assertEqual(res_my_comm.status_code, 200)
        self.assertEqual(len(res_my_comm.json()), 1)
        self.assertEqual(res_my_comm.json()[0]["id"], "test-channel")

if __name__ == '__main__':
    unittest.main()
