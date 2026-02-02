import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.models.models import User, Bill, Appliance, WeatherData
from beanie import init_beanie

async def check_latest_bill():
    print("DEBUG: Connecting to MongoDB...")
    client = AsyncIOMotorClient(settings.DATABASE_URL)
    await init_beanie(
        database=client.utility_analyzer,
        document_models=[User, Bill, Appliance, WeatherData]
    )
    
    print("\n--- Absolute Last Uploaded Bill ---")
    # Find the very last bill uploaded by ANYONE
    last_bill = await Bill.find_all().sort("-uploaded_at").first_or_none()
    
    if last_bill:
        print(f"ID: {last_bill.id}")
        print(f"User ID: {last_bill.user_id}")
        print(f"Type: {last_bill.bill_type}")
        print(f"Units: {last_bill.units_consumed}")
        print(f"Amount: {last_bill.total_amount}")
        print(f"Uploaded At: {last_bill.uploaded_at}")
        
        # Also check user info
        user = await User.get(last_bill.user_id)
        if user:
            print(f"User: {user.username} ({user.email})")
        else:
            print("User: NOT FOUND")
    else:
        print("No bills found in database.")

if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.getcwd())
    asyncio.run(check_latest_bill())
