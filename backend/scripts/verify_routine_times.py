import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import time

load_dotenv()

async def wait_and_check():
    # Wait a bit for routines to be created
    print("⏳ Waiting 5 seconds for routines to be created...")
    await asyncio.sleep(5)
    
    # Connect to MongoDB
    mongo_uri = os.getenv("MONGO_URI")
    client = AsyncIOMotorClient(mongo_uri)
    db = client.lifepilot
    
    print("\n🔍 Checking routine times in database...\n")
    
    routines = await db.routines.find({}).sort("_time_of_day", 1).to_list(length=100)
    
    if not routines:
        print("❌ No routines found in database yet. Please refresh the frontend to create default routines.")
        client.close()
        return
    
    print(f"✅ Found {len(routines)} routine(s)\n")
    
    for i, routine in enumerate(routines, 1):
        print(f"{i}. 📋 {routine.get('title', 'Unknown')}")
        print(f"   _time_of_day (24h): {routine.get('_time_of_day', 'NOT SET')}")
        print(f"   _end_time (24h): {routine.get('_end_time', 'NOT SET')}")
        print(f"   startTime (display): {routine.get('startTime', 'NOT SET')}")
        print(f"   endTime (display): {routine.get('endTime', 'NOT SET')}")
        print()
    
    # Verify sorting
    times = [r.get('_time_of_day') for r in routines if r.get('_time_of_day')]
    if times == sorted(times):
        print("✅ Routines are correctly sorted by _time_of_day!")
    else:
        print("❌ Routines are NOT sorted correctly!")
        print(f"   Expected: {sorted(times)}")
        print(f"   Actual: {times}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(wait_and_check())
