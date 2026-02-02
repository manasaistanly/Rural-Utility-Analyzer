import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.models.models import User, Bill, Appliance, WeatherData
from beanie import init_beanie

async def check_dates():
    client = AsyncIOMotorClient(settings.DATABASE_URL)
    await init_beanie(
        database=client.utility_analyzer,
        document_models=[User, Bill, Appliance, WeatherData]
    )
    
    print("\n--- Current Bill Dates ---")
    bills = await Bill.find_all().to_list()
    if not bills:
        print("No bills found.")
        return

    for bill in bills:
        print(f"ID: {bill.id} | Date: {bill.bill_date} | Type: {bill.bill_type} | Units: {bill.units_consumed}")

if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.getcwd())
    asyncio.run(check_dates())
