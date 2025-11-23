
import os
import sys
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

load_dotenv('backend/.env')

from app.core.embeddings import get_embeddings

def test_gemini_embeddings():
    print("Testing Gemini Embeddings...")
    
    # Force reload embeddings to pick up new env vars
    from app.core import embeddings
    embeddings.reset_embeddings()
    
    embed_service = get_embeddings()
    
    print(f"Provider: {embed_service.provider_name}")
    
    text = "Hello, world!"
    # Access the provider directly to see raw output if possible, or just print what we get
    embedding = embed_service.embed_single(text)
    
    print(f"Raw embedding type: {type(embedding)}")
    print(f"Embedding length: {len(embedding)}")
    if len(embedding) > 0:
        print(f"First element type: {type(embedding[0])}")
        if isinstance(embedding[0], list):
             print(f"Nested list detected. Inner length: {len(embedding[0])}")
    
    print(f"First 5 values: {embedding[:5]}")
    
    if len(embedding) == 768:
        print("SUCCESS: Embedding dimension is 768")
    else:
        print(f"WARNING: Unexpected dimension {len(embedding)}")

if __name__ == "__main__":
    test_gemini_embeddings()
