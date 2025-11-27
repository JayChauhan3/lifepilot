#!/usr/bin/env python3
"""
Check MongoDB Atlas database for routines
"""
import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

mongo_uri = os.getenv("MONGODB_URI")
if not mongo_uri:
    print("Error: MONGODB_URI not found")
    exit(1)

# Connect to MongoDB Atlas
client = MongoClient(mongo_uri)
db = client['lifepilot_test_db']
routines = db['routines']

# Get all routines
all_routines = list(routines.find({}))

print(f"Found {len(all_routines)} routines in Atlas database (lifepilot_test_db)\n")

for routine in all_routines:
    print(f"Routine: {routine.get('title', 'NO TITLE')}")
    print(f"  _id: {routine.get('_id')}")
    print(f"  startTime: {routine.get('startTime', 'MISSING')}")
    print(f"  endTime: {routine.get('endTime', 'MISSING')}")
    print()
