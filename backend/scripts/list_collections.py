#!/usr/bin/env python3
"""
List all collections in both databases
"""
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')

print("=== lifepilot_db ===")
db1 = client['lifepilot_db']
collections1 = db1.list_collection_names()
print(f"Collections: {collections1}")
for coll_name in collections1:
    count = db1[coll_name].count_documents({})
    print(f"  {coll_name}: {count} documents")

print("\n=== lifepilot_test_db ===")
db2 = client['lifepilot_test_db']
collections2 = db2.list_collection_names()
print(f"Collections: {collections2}")
for coll_name in collections2:
    count = db2[coll_name].count_documents({})
    print(f"  {coll_name}: {count} documents")
