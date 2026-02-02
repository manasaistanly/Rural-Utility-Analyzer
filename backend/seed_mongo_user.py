import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.models.models import User, Bill, Appliance, WeatherData
from app.core.security import get_password_hash
from beanie import init_beanie

async def seed_user():
    print("DEBUG: Connecting to MongoDB...")
    client = AsyncIOMotorClient(settings.DATABASE_URL)
    await init_beanie(
        database=client.utility_analyzer,
        document_models=[User, Bill, Appliance, WeatherData]
    )
    
    username = "demo"
    password = "demo123"
    
    # Check if user exists
    user = await User.find_one(User.username == username)
    if user:
        print(f"✅ User '{username}' already exists.")
        # Optional: Print info to verify
        print(f"   ID: {user.id}")
        print(f"   Email: {user.email}")
    else:
        print(f"Creating user '{username}'...")
        hashed_password = get_password_hash(password)
        new_user = User(
            username=username,
            email="demo@example.com",
            hashed_password=hashed_password,
            language_pref="en"
        )
        await new_user.insert()
        print(f"✅ Successfully created user '{username}' with password '{password}'")

if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.getcwd())
    asyncio.run(seed_user())
