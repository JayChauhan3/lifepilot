#!/usr/bin/env python3
"""
Script to migrate data from lifepilot_test_db to lifepilot_db.
1. Clears lifepilot_db.
2. Copies data from lifepilot_test_db to lifepilot_db.
3. Verifies counts.
4. Clears lifepilot_test_db.
"""
import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
import certifi
from dotenv import load_dotenv

load_dotenv()

async def migrate_database():
    """Migrate data from test db to prod db"""
    mongo_uri = os.getenv("MONGODB_URI")
    if not mongo_uri:
        print("❌ MONGODB_URI not set in environment")
        return

    print("🔌 Connecting to MongoDB...")
    client = AsyncIOMotorClient(mongo_uri, tlsCAFile=certifi.where())
    
    source_db_name = "lifepilot_test_db"
    target_db_name = "lifepilot_db"
    
    try:
        source_db = client[source_db_name]
        target_db = client[target_db_name]
        
        # Check source data
        source_collections = await source_db.list_collection_names()
        if not source_collections:
            print(f"⚠️  Source database '{source_db_name}' is empty. Nothing to migrate.")
            return

        print(f"\n📋 Found {len(source_collections)} collection(s) in source '{source_db_name}':")
        for coll in source_collections:
            count = await source_db[coll].count_documents({})
            print(f"  - {coll}: {count} document(s)")

        # Confirm migration
        print(f"\n⚠️  WARNING: This will:")
        print(f"  1. DELETE ALL data in target '{target_db_name}'")
        print(f"  2. Copy data from '{source_db_name}' to '{target_db_name}'")
        print(f"  3. DELETE ALL data in source '{source_db_name}' (after verification)")
        confirm = input("Type 'MIGRATE' to confirm: ")
        
        if confirm != "MIGRATE":
            print("❌ Cancelled")
            return

        # 1. Clear target DB
        print(f"\n🗑️  Clearing target database '{target_db_name}'...")
        target_collections = await target_db.list_collection_names()
        for coll in target_collections:
            await target_db[coll].drop()
            print(f"  ✓ Dropped {coll} from target")
            
        # 2. Migrate data
        print(f"\n🚀 Starting migration...")
        migrated_collections = []
        for coll_name in source_collections:
            cursor = source_db[coll_name].find({})
            docs = await cursor.to_list(length=None)
            
            if docs:
                await target_db[coll_name].insert_many(docs)
                count = len(docs)
                print(f"  ✓ Migrated {count} documents for '{coll_name}'")
                migrated_collections.append(coll_name)
            else:
                print(f"  ⚠️  Skipping empty collection '{coll_name}'")

        # 3. Verify
        print(f"\n🔍 Verifying migration...")
        verification_passed = True
        for coll_name in migrated_collections:
            source_count = await source_db[coll_name].count_documents({})
            target_count = await target_db[coll_name].count_documents({})
            
            if source_count == target_count:
                print(f"  ✅ {coll_name}: {target_count} matches")
            else:
                print(f"  ❌ {coll_name}: MISMATCH! Source: {source_count}, Target: {target_count}")
                verification_passed = False
        
        if not verification_passed:
            print("\n❌ Verification failed! Aborting source cleanup.")
            print("please check databases manually.")
            return

        # 4. Cleanup source DB
        print(f"\n🧹 Cleaning up source database '{source_db_name}'...")
        for coll in source_collections:
            await source_db[coll].drop()
            print(f"  ✓ Dropped {coll} from source")
            
        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(migrate_database())
