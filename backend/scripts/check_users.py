#!/usr/bin/env python3
"""
Check users and create default routines
"""
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['lifepilot_test_db']
users = db['users']
routines = db['routines']

# Get all users
all_users = list(users.find({}))

print(f"Found {all_users} users in database\n")

for user in all_users:
    print(f"User: {user.get('email', 'NO EMAIL')}")
    print(f"  user_id: {user.get('user_id')}")
    print(f"  is_verified: {user.get('is_verified')}")
    print()

# Check routines count
routine_count = routines.count_documents({})
print(f"\nTotal routines in database: {routine_count}")
