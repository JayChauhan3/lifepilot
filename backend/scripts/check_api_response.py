import asyncio
import sys
import os
import json
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import connect_to_mongo
from app.services.routine_service import RoutineService

async def check_api_response():
    await connect_to_mongo()
    
    # Use the new user ID from the logs
    user_id = "83697626-5772-4ed1-9261-09a000473672"
    
    service = RoutineService()
    routines = await service.get_routines(user_id)
    
    print(f"\n=== API RESPONSE ({len(routines)} routines) ===\n")
    
    for routine in routines:
        # This is what FastAPI sends to the frontend
        data = routine.model_dump(by_alias=True)
        
        print(f"Title: {data.get('title')}")
        print(f"  startTime: {data.get('startTime')}")
        print(f"  endTime: {data.get('endTime')}")
        print(f"  duration: {data.get('duration')}")
        print(f"  canDelete: {data.get('canDelete')}")
        print(f"  canEditTitle: {data.get('canEditTitle')}")
        print(f"  icon: {data.get('icon')}")
        print()

if __name__ == "__main__":
    asyncio.run(check_api_response())
