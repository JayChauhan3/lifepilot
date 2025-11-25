import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

async def check_routines():
    # Connect to MongoDB
    mongo_uri = os.getenv("MONGO_URI")
    client = AsyncIOMotorClient(mongo_uri)
    db = client.lifepilot
    
    print("🔍 Checking routine times in database...\n")
    
    routines = await db.routines.find({}).to_list(length=100)
    
    for routine in routines:
        print(f"📋 {routine.get('title', 'Unknown')}")
        print(f"   _time_of_day: {routine.get('_time_of_day', 'NOT SET')}")
        print(f"   time_of_day: {routine.get('time_of_day', 'NOT SET')}")
        print(f"   startTime: {routine.get('startTime', 'NOT SET')}")
        print(f"   _end_time: {routine.get('_end_time', 'NOT SET')}")
        print(f"   end_time: {routine.get('end_time', 'NOT SET')}")
        print()
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_routines())
