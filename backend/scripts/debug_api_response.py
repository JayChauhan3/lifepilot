import asyncio
import sys
import os
import json
from dotenv import load_dotenv

# Load env vars
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import connect_to_mongo
from app.services.routine_service import RoutineService

async def debug_api_response():
    print("Debugging Routine Service Output...")
    
    # Connect to DB
    await connect_to_mongo()
    
    # Use the user ID from previous steps
    user_id = "726b0684-655b-4002-a85d-691ff8b2ba39"
    
    # Inspect raw documents
    from app.core.database import db
    database = db.client[db.db_name]
    raw_routines = await database.routines.find({"user_id": user_id}).to_list(length=100)
    print(f"\n--- RAW MONGODB DOCUMENTS ({len(raw_routines)}) ---")
    for r in raw_routines:
        print(f"ID: {r.get('_id')}")
        print(f"Keys: {list(r.keys())}")
        print(f"time_of_day: {r.get('time_of_day')}")
        print(f"_time_of_day: {r.get('_time_of_day')}")
        print(f"startTime: {r.get('startTime')}")
        print("-" * 20)

if __name__ == "__main__":
    asyncio.run(debug_api_response())
