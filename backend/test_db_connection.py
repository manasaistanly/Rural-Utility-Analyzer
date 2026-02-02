import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.models.models import User, Bill, Appliance, WeatherData
from beanie import init_beanie

async def test_connection():
    print(f"DEBUG: DATABASE_URL from settings: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else '...'}")
    
    try:
        print("DEBUG: Creating AsyncIOMotorClient...")
        client = AsyncIOMotorClient(settings.DATABASE_URL, serverSelectionTimeoutMS=5000)
        
        print("DEBUG: Pinging server...")
        # Force a connection attempt
        await client.admin.command('ping')
        print("✅ MongoDB Connection Successful (Ping OK)")
        
        print("DEBUG: Initializing Beanie...")
        await init_beanie(
            database=client.utility_analyzer,
            document_models=[User, Bill, Appliance, WeatherData]
        )
        print("✅ Beanie Initialization Successful")
        
    except Exception as e:
        print(f"❌ CONNECTION FAILED: {e}")

if __name__ == "__main__":
    # Ensure loaded modules find the 'app' package
    import sys
    import os
    sys.path.append(os.getcwd())
    
    asyncio.run(test_connection())
