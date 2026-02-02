import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.models.models import User, Bill, Appliance, WeatherData
from beanie import init_beanie

async def clean_invalid_bills():
    print("DEBUG: Connecting to MongoDB...")
    client = AsyncIOMotorClient(settings.DATABASE_URL)
    await init_beanie(
        database=client.utility_analyzer,
        document_models=[User, Bill, Appliance, WeatherData]
    )
    
    print("\n--- Cleaning Invalid Bills ---")
    # Delete bills where units_consumed is 0 OR total_amount is 0
    # Note: Using $or operator for MongoDB query
    result = await Bill.find(
        {"$or": [
            {"units_consumed": 0},
            {"total_amount": 0}
        ]}
    ).delete()
    
    if result.deleted_count > 0:
        print(f"✅ Deleted {result.deleted_count} invalid bills (0 units/amount).")
    else:
        print("No invalid bills found.")
        
    print("\nRemaining Bills:")
    remaining = await Bill.find_all().to_list()
    for bill in remaining:
        print(f"ID: {bill.id} | Type: {bill.bill_type} | Units: {bill.units_consumed} | Amount: ₹{bill.total_amount}")

if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.getcwd())
    asyncio.run(clean_invalid_bills())
