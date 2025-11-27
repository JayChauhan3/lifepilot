import asyncio
import sys
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import connect_to_mongo, db
from app.utils.seed_routines import seed_default_routines

async def fix_current_user():
    await connect_to_mongo()
    
    user_id = "83697626-5772-4ed1-9261-09a000473672"
    
    database = db.client[db.db_name]
    
    # Delete all existing routines
    result = await database.routines.delete_many({"user_id": user_id})
    print(f"Deleted {result.deleted_count} routines")
    
    # Re-seed with correct data
    created = await seed_default_routines(user_id)
    print(f"Created {len(created)} routines")
    
    # Verify
    from app.services.routine_service import RoutineService
    service = RoutineService()
    routines = await service.get_routines(user_id)
    
    print("\n=== VERIFICATION ===")
    for r in routines:
        data = r.model_dump(by_alias=True)
        print(f"{data['title']}: startTime={data.get('startTime')}, canDelete={data.get('canDelete')}")

if __name__ == "__main__":
    asyncio.run(fix_current_user())
