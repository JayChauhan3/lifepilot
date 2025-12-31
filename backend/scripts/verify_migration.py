#!/usr/bin/env python3
"""
Script to verify database migration status.
"""
import asyncio
import os
import sys
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
import certifi
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))
load_dotenv()

async def verify_migration():
    mongo_uri = os.getenv("MONGODB_URI")
    client = AsyncIOMotorClient(mongo_uri, tlsCAFile=certifi.where())
    
    test_db = client["lifepilot_test_db"]
    prod_db = client["lifepilot_db"]
    
    print("--- Database Verification Status ---")
    
    # Check Source (Test DB)
    test_colls = await test_db.list_collection_names()
    print(f"\n[Source] lifepilot_test_db:")
    if not test_colls:
        print("  (Empty) - This is GOOD if migration finished.")
    else:
        for coll in test_colls:
            count = await test_db[coll].count_documents({})
            print(f"  - {coll}: {count}")

    # Check Target (Prod DB)
    prod_colls = await prod_db.list_collection_names()
    print(f"\n[Target] lifepilot_db:")
    if not prod_colls:
        print("  (Empty) - This is BAD if migration finished.")
    else:
        for coll in prod_colls:
            count = await prod_db[coll].count_documents({})
            print(f"  - {coll}: {count}")
            
    client.close()

if __name__ == "__main__":
    asyncio.run(verify_migration())
