#!/usr/bin/env python3

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from app.core.llm_service import get_llm_service

def test_gemini():
    """Test Gemini API directly"""
    print("Testing Gemini API...")
    
    # Check environment variables
    print(f"LLM_PROVIDER: {os.getenv('LLM_PROVIDER')}")
    print(f"GEMINI_API_KEY: {'SET' if os.getenv('GEMINI_API_KEY') else 'NOT SET'}")
    
    # Get LLM service
    llm_service = get_llm_service()
    print(f"Provider: {llm_service.provider_name}")
    
    # Test simple generation
    try:
        response = llm_service.generate_text("What is AI? Answer in one sentence.", max_tokens=100)
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_gemini()
