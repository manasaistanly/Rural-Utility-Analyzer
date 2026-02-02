from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.core.config import settings
from app.models.models import User, Bill, Appliance, WeatherData

class Database:
    client: AsyncIOMotorClient = None

db = Database()

async def get_database():
    return db.client

async def connect_to_mongo():
    """Connect to MongoDB Atlas"""
    try:
        print(f"DEBUG: Attempting to connect to MongoDB...")
        # Mask password for logs
        masked_url = settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else "..."
        print(f"DEBUG: Connection URL (masked): ...@{masked_url}")
        
        db.client = AsyncIOMotorClient(settings.DATABASE_URL)
        print("DEBUG: Client created, initializing Beanie...")
        
        await init_beanie(
            database=db.client.utility_analyzer,
            document_models=[User, Bill, Appliance, WeatherData]
        )
        print("✅ Connected to MongoDB Atlas!")
    except Exception as e:
        print(f"❌ MongoDB Connection Error: {e}")

async def close_mongo_connection():
    """Close MongoDB connection"""
    db.client.close()
    print("❌ Closed MongoDB connection")
