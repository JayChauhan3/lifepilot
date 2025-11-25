"""
Script to inspect routine documents in the database
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import json

from pathlib import Path

# Load .env from parent directory
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

async def inspect_routines():
    mongo_uri = os.getenv("MONGODB_URI")
    print(f"Connecting to MongoDB...")
    # Mask password in URI for printing
    safe_uri = mongo_uri.split('@')[-1] if '@' in mongo_uri else 'localhost'
    print(f"URI host: {safe_uri}")
    
    client = AsyncIOMotorClient(mongo_uri)
    db = client.lifepilot_db
    
    print(f"Database: {db.name}")
    collections = await db.list_collection_names()
    print(f"Collections: {collections}")
    
    count = await db.routines.count_documents({})
    print(f"Total routines in DB: {count}")
    
    print("\n🔍 Inspecting all routines in database...\n")
    
    routines = await db.routines.find({}).to_list(length=1000)
    
    for i, routine in enumerate(routines, 1):
        print(f"Routine #{i}:")
        print(f"  Keys: {list(routine.keys())}")
        print(f"  Full doc: {routine}")
        print()
    
    client.close()

if __name__ == "__main__":
    asyncio.run(inspect_routines())
