"""
Script to fix existing routines by populating _time_of_day and _end_time fields
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from datetime import datetime

from pathlib import Path

# Manually read .env file
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value
                print(f"Loaded key: {key}")
else:
    print(f"❌ Error: .env file not found at {env_path}")

def _to_24h(time_str: str) -> str:
    """Convert 12h time string to 24h format"""
    if not time_str:
        return time_str
    
    # Try with space first (e.g., "2:00 PM")
    try:
        time_obj = datetime.strptime(time_str, '%I:%M %p')
        return time_obj.strftime('%H:%M')
    except (ValueError, TypeError):
        pass
    
    # Try without space (e.g., "2:00PM")
    try:
        time_obj = datetime.strptime(time_str, '%I:%M%p')
        return time_obj.strftime('%H:%M')
    except (ValueError, TypeError):
        pass
    
    # If both fail, assume it's already in 24h format or invalid
    return time_str

async def fix_routines():
    # Connect to MongoDB
    mongo_uri = os.getenv("MONGODB_URI")
    if not mongo_uri:
        print("❌ Error: MONGODB_URI not found in .env")
        return

    client = AsyncIOMotorClient(mongo_uri)
    db = client.lifepilot_db
    
    print(f"Connected to DB: {db.name}")
    
    print(f"Connected to DB: {db.name}")
    print(f"Collections: {await db.list_collection_names()}")
    
    count = await db.routines.count_documents({})
    print(f"Total routines found: {count}")
    
    print("🔍 Finding routines with missing time fields...")
    
    routines = await db.routines.find({}).to_list(length=1000)
    
    fixed_count = 0
    # Default times map
    default_times = {
        "Morning Routine": ("6:00 AM", "10:00 AM"),
        "Work Block": ("10:00 AM", "5:00 PM"),
        "Evening Routine": ("5:00 PM", "10:00 PM"),
        "Sleep": ("10:00 PM", "6:00 AM")
    }

    for routine in routines:
        title = routine.get('title', 'Unknown')
        # Check for time_of_day (backend field) or startTime (frontend field)
        start_time = routine.get('time_of_day') or routine.get('startTime')
        end_time = routine.get('end_time') or routine.get('endTime')
        
        # If times are missing, try to use defaults
        if not start_time and title in default_times:
            start_time = default_times[title][0]
            print(f"  Using default start time for '{title}': {start_time}")
            
        if not end_time and title in default_times:
            end_time = default_times[title][1]
            print(f"  Using default end time for '{title}': {end_time}")
        
        # Check if _time_of_day or _end_time is missing
        if start_time and not routine.get('_time_of_day'):
            _time_of_day = _to_24h(start_time)
            print(f"  Fixing '{title}': start={start_time} -> _time_of_day={_time_of_day}")
            await db.routines.update_one(
                {"_id": routine["_id"]},
                {"$set": {"_time_of_day": _time_of_day, "startTime": start_time, "time_of_day": start_time}}
            )
            fixed_count += 1
        
        if end_time and not routine.get('_end_time'):
            _end_time = _to_24h(end_time)
            print(f"  Fixing '{title}': end={end_time} -> _end_time={_end_time}")
            await db.routines.update_one(
                {"_id": routine["_id"]},
                {"$set": {"_end_time": _end_time, "endTime": end_time, "end_time": end_time}}
            )
            fixed_count += 1
    
    print(f"\n✅ Fixed {fixed_count} time fields!")
    
    # Verify
    print("\n🔍 Verifying fixes...")
    routines = await db.routines.find({}).to_list(length=1000)
    for routine in routines:
        title = routine.get('title', 'Unknown')
        print(f"  {title}: _time_of_day={routine.get('_time_of_day')}, _end_time={routine.get('_end_time')}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_routines())
