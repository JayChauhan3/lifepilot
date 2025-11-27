#!/usr/bin/env python3
"""
List all databases and their collections
"""
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')

# List all databases
db_names = client.list_database_names()
print(f"All databases: {db_names}\n")

for db_name in db_names:
    if 'lifepilot' in db_name.lower() or db_name not in ['admin', 'config', 'local']:
        print(f"=== {db_name} ===")
        db = client[db_name]
        collections = db.list_collection_names()
        print(f"Collections: {collections}")
        
        for coll_name in collections:
            count = db[coll_name].count_documents({})
            print(f"  {coll_name}: {count} documents")
            
            # Show sample data for routines
            if coll_name == 'routines' and count > 0:
                sample = db[coll_name].find_one({})
                if sample:
                    print(f"    Sample: title={sample.get('title')}, startTime={sample.get('startTime')}, endTime={sample.get('endTime')}")
        print()
