import asyncio
import sys
import os
from dotenv import load_dotenv

# Load env vars
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import connect_to_mongo, db
from app.utils.seed_routines import seed_default_routines

async def fix_routines():
    print("Fixing routines...")
    await connect_to_mongo()
    
    user_id = "726b0684-655b-4002-a85d-691ff8b2ba39"
    
    # Delete existing broken routines
    database = db.client[db.db_name]
    result = await database.routines.delete_many({"user_id": user_id})
    print(f"Deleted {result.deleted_count} broken routines.")
    
    # Re-seed
    created = await seed_default_routines(user_id)
    print(f"Seeded {len(created)} new routines.")
    
    # Verify
    routines = await database.routines.find({"user_id": user_id}).to_list(length=10)
    for r in routines:
        print(f"Routine: {r.get('title')}")
        print(f"  _time_of_day: {r.get('_time_of_day')}")
        print(f"  startTime: {r.get('startTime')}") # Should be present if model_dump worked, or None if raw
        print(f"  canDelete: {r.get('canDelete')}")

if __name__ == "__main__":
    asyncio.run(fix_routines())
