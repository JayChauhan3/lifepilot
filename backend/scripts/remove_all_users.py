kill -9 86577#!/usr/bin/env python3
"""
Script to remove all user accounts from the database.
WARNING: This will permanently delete all user data.
"""
import asyncio
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent.absolute())
sys.path.insert(0, project_root)

from app.core.database import connect_to_mongo, close_mongo_connection, get_database
from app.config import settings
import structlog

logger = structlog.get_logger()

async def remove_all_users():
    """Remove all user accounts from the database."""
    try:
        # Connect to MongoDB
        await connect_to_mongo()
        db = get_database()
        
        if not db:
            logger.error("Failed to connect to the database")
            return False
        
        # Collections to clean up
        collections_to_clean = [
            "users",
            "pending_registrations",
            "sessions",
            "tokens",
            "routines",
            "tasks",
            # Add any other collections that contain user-specific data
        ]
        
        # Delete data from each collection
        for collection_name in collections_to_clean:
            try:
                result = await db[collection_name].delete_many({})
                logger.info(
                    f"Removed {result.deleted_count} documents from {collection_name} collection"
                )
            except Exception as e:
                logger.error(
                    f"Error removing documents from {collection_name}", 
                    error=str(e)
                )
        
        logger.info("Successfully removed all user accounts and related data")
        return True
        
    except Exception as e:
        logger.error("Error removing users", error=str(e))
        return False
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    print("WARNING: This will permanently delete ALL user accounts and related data!")
    confirmation = input("Are you sure you want to continue? (yes/no): ")
    
    if confirmation.lower() == 'yes':
        print("Removing all user accounts...")
        success = asyncio.run(remove_all_users())
        if success:
            print("Successfully removed all user accounts and related data.")
        else:
            print("Failed to remove user accounts. Check the logs for details.")
            sys.exit(1)
    else:
        print("Operation cancelled.")
        sys.exit(0)
