#!/usr/bin/env python3
"""
Test script to check what the routines API is returning
"""
import asyncio
import sys
sys.path.insert(0, '/Users/jaychauhan/Documents/GitHub/lifepilot/backend')

from app.core.database import db
from app.services.routine_service import RoutineService
import json

async def test_routines():
    # Connect to database
    await db.connect()
    
    # Get a user_id from the database
    users_collection = db.client[db.db_name].users
    user = await users_collection.find_one({})
    
    if not user:
        print("No users found in database")
        return
    
    user_id = user['user_id']
    print(f"Testing with user_id: {user_id}\n")
    
    # Get routines
    routine_service = RoutineService()
    routines = await routine_service.get_routines(user_id)
    
    print(f"Found {len(routines)} routines\n")
    
    for routine in routines:
        print(f"Routine: {routine.title}")
        print(f"  ID: {routine.id}")
        
        # Check what fields exist
        dumped = routine.model_dump()
        print(f"  startTime in dump: {dumped.get('startTime', 'MISSING')}")
        print(f"  endTime in dump: {dumped.get('endTime', 'MISSING')}")
        
        # Check raw attributes
        print(f"  routine.startTime attr: {getattr(routine, 'startTime', 'MISSING')}")
        print(f"  routine.endTime attr: {getattr(routine, 'endTime', 'MISSING')}")
        print()
    
    await db.disconnect()

if __name__ == "__main__":
    asyncio.run(test_routines())
