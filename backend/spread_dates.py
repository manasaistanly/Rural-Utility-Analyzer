import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.models.models import User, Bill, Appliance, WeatherData
from beanie import init_beanie
from datetime import date, timedelta
import random

async def spread_dates():
    client = AsyncIOMotorClient(settings.DATABASE_URL)
    await init_beanie(
        database=client.utility_analyzer,
        document_models=[User, Bill, Appliance, WeatherData]
    )
    
    print("\n--- Spreading Bill Dates ---")
    bills = await Bill.find_all().to_list()
    
    # Sort bills by ID (preserve upload order roughly)
    bills.sort(key=lambda x: x.id)
    
    # Generate dates for the last 6 months
    today = date.today()
    
    for i, bill in enumerate(bills):
        # Assign each bill to a distinct month going backwards
        # e.g. Bill 1 -> This month, Bill 2 -> Last month, etc.
        # Or mostly random within last year
        
        month_offset = i % 12 # Cycle through 12 months
        target_date = today - timedelta(days=30 * month_offset)
        
        # Add some jitter (+- 5 days)
        jitter = random.randint(-5, 5)
        new_date = target_date + timedelta(days=jitter)
        
        bill.bill_date = new_date
        await bill.save()
        print(f"Updated Bill {bill.id} -> {new_date}")

    print(f"\n✅ Successfully redistributed {len(bills)} bills across different months.")

if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.getcwd())
    asyncio.run(spread_dates())
