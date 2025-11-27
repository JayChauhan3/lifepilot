#!/usr/bin/env python3
"""
Check MongoDB routines collection directly
"""
from pymongo import MongoClient
import json

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['lifepilot_test_db']  # Changed to correct database
routines = db['routines']

# Get all routines
all_routines = list(routines.find({}))

print(f"Found {len(all_routines)} routines in database\n")

for routine in all_routines:
    print(f"Routine: {routine.get('title', 'NO TITLE')}")
    print(f"  _id: {routine.get('_id')}")
    print(f"  user_id: {routine.get('user_id')}")
    print(f"  startTime: {routine.get('startTime', 'MISSING')}")
    print(f"  endTime: {routine.get('endTime', 'MISSING')}")
    print(f"  time_of_day: {routine.get('time_of_day', 'MISSING')}")
    print(f"  end_time: {routine.get('end_time', 'MISSING')}")
    print(f"  time_of_day_24h: {routine.get('time_of_day_24h', 'MISSING')}")
    print(f"  end_time_24h: {routine.get('end_time_24h', 'MISSING')}")
    print()
