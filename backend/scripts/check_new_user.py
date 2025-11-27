import asyncio
import sys
import os
import json
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import connect_to_mongo
from app.services.routine_service import RoutineService

async def check_new_user():
    await connect_to_mongo()
    
    # New user from logs
    user_id = "6e6a4ea9-26c6-49ed-ba66-db8336fc0a72"
    
    service = RoutineService()
    routines = await service.get_routines(user_id)
    
    print(f"\n=== API RESPONSE FOR NEW USER ({len(routines)} routines) ===\n")
    
    for routine in routines:
        data = routine.model_dump(by_alias=True)
        
        print(f"Title: {data.get('title')}")
        print(f"  startTime: {data.get('startTime')}")
        print(f"  endTime: {data.get('endTime')}")
        print(f"  duration: {data.get('duration')}")
        print(f"  canDelete: {data.get('canDelete')}")
        print(f"  icon: {data.get('icon')}")
        print(f"  Full JSON: {json.dumps(data, indent=2, default=str)}")
        print()

if __name__ == "__main__":
    asyncio.run(check_new_user())
