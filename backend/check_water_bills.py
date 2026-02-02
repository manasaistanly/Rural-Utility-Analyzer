import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.models.models import User, Bill, Appliance, WeatherData
from beanie import init_beanie

async def check_water_bills():
    print("DEBUG: Connecting to MongoDB...")
    client = AsyncIOMotorClient(settings.DATABASE_URL)
    await init_beanie(
        database=client.utility_analyzer,
        document_models=[User, Bill, Appliance, WeatherData]
    )
    
    print("\n--- Recent Water Bills ---")
    # Find all bills with type 'water'
    water_bills = await Bill.find(Bill.bill_type == "water").sort("-bill_date").to_list()
    
    if water_bills:
        print(f"Found {len(water_bills)} water bills:")
        for bill in water_bills:
            print(f"ID: {bill.id} | Date: {bill.bill_date} | Units: {bill.units_consumed} KL | Amount: ₹{bill.total_amount}")
    else:
        print("No water bills found.")

if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.getcwd())
    asyncio.run(check_water_bills())
