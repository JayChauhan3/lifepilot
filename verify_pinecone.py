
import os
import sys
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

load_dotenv('backend/.env')

from app.core.memory_bank import get_memory_bank

def verify_pinecone_setup():
    print("Verifying Pinecone Setup...")
    
    # Initialize Memory Bank
    memory_bank = get_memory_bank()
    
    if memory_bank._vector_index:
        print("SUCCESS: Pinecone Index initialized")
    else:
        print("ERROR: Pinecone Index NOT initialized")
        return

    # Test Storing Memory
    user_id = "test_user"
    key = "test_memory_key"
    value = "This is a test memory to verify Pinecone integration."
    
    print(f"Storing memory for user: {user_id}")
    success = memory_bank.store_memory(user_id, key, value)
    
    if success:
        print("SUCCESS: Memory stored (and upserted to Pinecone)")
    else:
        print("ERROR: Failed to store memory")
        return

    # Test Retrieval
    print("Testing Retrieval...")
    query = "verify integration"
    results = memory_bank.retrieve_similar_memories(user_id, query)
    
    print(f"Retrieved {len(results)} results")
    for res in results:
        print(f" - Key: {res['key']}, Score: {res['distance']}")
        if res['key'] == key:
            print("SUCCESS: Test memory retrieved correctly")

if __name__ == "__main__":
    verify_pinecone_setup()
