#!/usr/bin/env python3
"""
Script to sync memories from MongoDB (Source of Truth) to Pinecone (Search Index).
1. clear Pinecone index.
2. Read all memories from MongoDB.
3. Re-embed and upload to Pinecone.
"""
import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
import certifi
from pinecone import Pinecone
from dotenv import load_dotenv
from app.core.embeddings import get_embeddings

load_dotenv()

async def sync_memories():
    print("🔄 Starting Memory Sync...")
    
    # 1. Connect to MongoDB
    mongo_uri = os.getenv("MONGODB_URI")
    if not mongo_uri:
        print("❌ MONGODB_URI not set")
        return
        
    print("🔌 Connecting to MongoDB...")
    mongo_client = AsyncIOMotorClient(mongo_uri, tlsCAFile=certifi.where())
    db = mongo_client["lifepilot_db"]
    collection = db["memories"]
    
    # 2. Connect to Pinecone
    api_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX", "lifepilot-memory")
    if not api_key:
        print("❌ PINECONE_API_KEY not set")
        return
        
    print(f"🌲 Connecting to Pinecone (Index: {index_name})...")
    pc = Pinecone(api_key=api_key)
    index = pc.Index(index_name)
    
    # 3. Clear Pinecone
    print("🗑️  Clearing Pinecone index...")
    try:
        index.delete(delete_all=True)
        print("  ✓ Index cleared")
    except Exception as e:
        print(f"  ⚠️  Could not clear index (might be empty): {e}")

    # 4. Fetch from MongoDB
    print("📥 Fetching memories from MongoDB...")
    cursor = collection.find({})
    memories = await cursor.to_list(length=None)
    total_memories = len(memories)
    print(f"  📋 Found {total_memories} memories to sync")
    
    if total_memories == 0:
        print("✅ No memories to sync.")
        return

    # 5. Re-embed and Upload
    print("🚀 Re-embedding and uploading...")
    embeddings_service = get_embeddings()
    
    count = 0
    batch_size = 20
    batch = []
    
    for doc in memories:
        try:
            # Extract content
            user_id = doc.get("user_id")
            key = doc.get("key")
            value = doc.get("value")
            category = doc.get("category", "general")
            
            if not user_id or not key or not value:
                continue
                
            content = str(value)
            
            # Generate embedding
            vector = embeddings_service.embed_single(content)
            
            # Add to batch
            batch.append({
                "id": f"{user_id}_{key}",
                "values": vector,
                "metadata": {
                    "user_id": user_id,
                    "key": key,
                    "category": category,
                    "content": content
                }
            })
            
            # Upload batch if full
            if len(batch) >= batch_size:
                index.upsert(vectors=batch)
                count += len(batch)
                print(f"  ✓ Synced {count}/{total_memories}")
                batch = []
                
        except Exception as e:
            print(f"  ❌ Error processing memory {doc.get('key')}: {e}")

    # Upload remaining
    if batch:
        index.upsert(vectors=batch)
        count += len(batch)
        print(f"  ✓ Synced {count}/{total_memories}")
        
    print("\n✅ Sync Completed Successfully!")
    print(f"  - Source (MongoDB): {total_memories} docs")
    print(f"  - Target (Pinecone): {count} vectors")

if __name__ == "__main__":
    asyncio.run(sync_memories())
