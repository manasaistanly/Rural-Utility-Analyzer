"""
Quick script to create a test user for login
"""
import asyncio
from app.core.database import connect_to_mongo
from app.models.models import User
from app.core.security import get_password_hash

async def create_test_user():
    await connect_to_mongo()
    
    # Check if user exists
    existing_user = await User.find_one(User.email == "test@example.com")
    if existing_user:
        print("❌ User test@example.com already exists!")
        print(f"User ID: {existing_user.id}")
        print(f"Username: {existing_user.username}")
        return
    
    # Create test user
    hashed_password = get_password_hash("password123")
    test_user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=hashed_password,
        role="CONSUMER"
    )
    await test_user.insert()
    print("✅ Test user created successfully!")
    print(f"Email: test@example.com")
    print(f"Password: password123")
    print(f"Username: testuser")

if __name__ == "__main__":
    asyncio.run(create_test_user())
