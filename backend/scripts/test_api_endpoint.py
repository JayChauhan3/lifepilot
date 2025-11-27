import asyncio
import sys
import os
import json
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import connect_to_mongo
from app.api.routines import get_routines
from app.models import UserModel

async def test_api_endpoint():
    await connect_to_mongo()
    
    # Create a mock user
    user = UserModel(
        user_id="6e6a4ea9-26c6-49ed-ba66-db8336fc0a72",
        email="test@test.com"
    )
    
    # Call the actual API endpoint function
    result = await get_routines(current_user=user)
    
    print("=== ACTUAL API ENDPOINT RESPONSE ===")
    print(json.dumps(result, indent=2, default=str))

if __name__ == "__main__":
    asyncio.run(test_api_endpoint())
