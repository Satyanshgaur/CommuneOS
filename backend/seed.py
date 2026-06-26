# backend/seed.py

from sqlalchemy.orm import Session
from backend.database import SessionLocal, engine, Base
from backend.models import User, Community, CommunityMember
from backend.auth import get_password_hash
from backend.mock_data import MEMBERS, COMMUNITIES

def seed_database(db: Session):
    # Check if we already have users
    if db.query(User).count() > 0:
        print("Database already seeded.")
        return

    print("Seeding database with mock data...")

    # Create users
    db_users = {}
    default_password_hash = get_password_hash("password123")

    for m_id, m_data in MEMBERS.items():
        skills_str = ",".join(m_data.get("skills", []))
        user = User(
            id=m_id,
            email=f"{m_id}@communityos.org",
            hashed_password=default_password_hash,
            full_name=m_data.get("name", m_id.capitalize()),
            bio=m_data.get("bio"),
            skills=skills_str,
            skill_level=m_data.get("skill_level", "Beginner"),
            goals=m_data.get("goals"),
            learning_style=m_data.get("learning_style")
        )
        db.add(user)
        db_users[m_id] = user

    # Create communities
    db_communities = {}
    for c_data in COMMUNITIES:
        c_id = c_data["id"]
        # Determine owner
        creator = "sarah" if c_id in ["systems-programming", "gpu-computing"] else "elena"
        if creator not in db_users:
            creator = list(db_users.keys())[0]

        community = Community(
            id=c_id,
            name=c_data["name"],
            category=c_data["category"],
            description=c_data["description"],
            created_by=creator
        )
        db.add(community)
        db_communities[c_id] = community

    # Flush so IDs are available
    db.commit()

    # Create memberships
    memberships = [
        ("rahul", "systems-programming", "Member"),
        ("rahul", "gpu-computing", "Member"),
        ("rahul", "ai-infrastructure", "Member"),
        ("priya", "pytorch-study-group", "Member"),
        ("priya", "machine-learning-basics", "Member"),
        ("priya", "ai-infrastructure", "Member"),
        ("sarah", "gpu-computing", "Owner"),
        ("sarah", "systems-programming", "Mentor"),
        ("elena", "pytorch-study-group", "Owner"),
        ("elena", "machine-learning-basics", "Mentor"),
        ("aman", "systems-programming", "Member"),
        ("vikram", "pytorch-study-group", "Member")
    ]

    for u_id, c_id, role in memberships:
        if u_id in db_users and c_id in db_communities:
            member = CommunityMember(
                user_id=u_id,
                community_id=c_id,
                role=role
            )
            db.add(member)

    db.commit()
    print("Database seeding completed.")

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
