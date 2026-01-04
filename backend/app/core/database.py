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
    db.client = AsyncIOMotorClient(settings.DATABASE_URL)
    await init_beanie(
        database=db.client.utility_analyzer,
        document_models=[User, Bill, Appliance, WeatherData]
    )
    print("✅ Connected to MongoDB Atlas!")

async def close_mongo_connection():
    """Close MongoDB connection"""
    db.client.close()
    print("❌ Closed MongoDB connection")
