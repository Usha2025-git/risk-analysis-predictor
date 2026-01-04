#!/usr/bin/env python3
"""
Create a demo user for testing the application.
Run this script to add a test user to the database.
"""
import uuid
from app.database import SessionLocal, init_db
from app.models.user import User
from app.core.security import get_password_hash

def create_demo_user():
    """Create a demo user for testing."""
    init_db()  # Ensure tables exist
    
    db = SessionLocal()
    try:
        # Check if demo user already exists
        existing_user = db.query(User).filter(User.username == "demo").first()
        if existing_user:
            print("Demo user already exists!")
            print(f"Username: demo")
            print(f"Email: demo@example.com")
            print(f"Password: demo123")
            return
        
        # Create demo user
        demo_user = User(
            id=str(uuid.uuid4()),
            email="demo@example.com",
            username="demo",
            full_name="Demo User",
            hashed_password=get_password_hash("demo123"),
            is_active=True,
            is_superuser=False
        )
        
        db.add(demo_user)
        db.commit()
        db.refresh(demo_user)
        
        print("✅ Demo user created successfully!")
        print(f"Username: demo")
        print(f"Email: demo@example.com")
        print(f"Password: demo123")
        print(f"User ID: {demo_user.id}")
        
    except Exception as e:
        print(f"❌ Error creating demo user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_demo_user()