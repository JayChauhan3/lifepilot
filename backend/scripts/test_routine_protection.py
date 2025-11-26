import asyncio
import sys
import os
from dotenv import load_dotenv

# Load env vars
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.models import RoutineModel
from app.utils.seed_routines import seed_default_routines, WORK_BLOCK_DEFAULT_ID
from app.core.database import connect_to_mongo, get_database

async def test_protection():
    print("Testing Routine Protection...")
    
    # Connect to DB
    await connect_to_mongo()
    db = get_database()
    
    # Mock user ID
    user_id = "test_user_protection"
    
    # Clear existing routines for test user
    await db.routines.delete_many({"user_id": user_id})
    
    # Seed routines
    routines = await seed_default_routines(user_id)
    print(f"Seeded {len(routines)} routines")
    
    # Verify Work Block protection
    work_block = next(r for r in routines if r.id == WORK_BLOCK_DEFAULT_ID)
    
    if not work_block.is_protected:
        print("FAIL: Work Block should be protected")
        return
        
    if work_block.can_delete:
        print("FAIL: Work Block should not be deletable")
        return
        
    if work_block.can_edit_title:
        print("FAIL: Work Block title should not be editable")
        return
        
    if not work_block.can_edit_time:
        print("FAIL: Work Block time SHOULD be editable")
        return
        
    print("PASS: Work Block protection flags correct")
    
    # Verify Morning Routine (should be unprotected)
    morning = next(r for r in routines if r.title == "Morning Routine")
    if not morning.can_delete:
        print("FAIL: Morning Routine should be deletable")
        return
        
    print("PASS: Morning Routine protection flags correct")
    
    # Clean up
    await db.routines.delete_many({"user_id": user_id})
    print("Test Complete")

if __name__ == "__main__":
    asyncio.run(test_protection())
