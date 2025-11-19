#!/usr/bin/env python3
"""
Test script for LifePilot API endpoints
"""

import requests
import json
import time

def test_api():
    """Test the API endpoints"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing LifePilot API...")
    print(f"   Base URL: {base_url}")
    
    # Test health endpoint
    print("\n📋 Testing Health Endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("   ✅ Health check passed")
            print(f"   📄 Response: {response.json()}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to server. Make sure the server is running:")
        print("       python start.py")
        return False
    
    # Test root endpoint
    print("\n📋 Testing Root Endpoint...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("   ✅ Root endpoint working")
            print(f"   📄 Response: {response.json()}")
        else:
            print(f"   ❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test chat endpoint
    print("\n📋 Testing Chat Endpoint...")
    chat_data = {
        "user_id": "api_test_user",
        "message": "Plan my morning routine"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/chat",
            json=chat_data,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            print("   ✅ Chat endpoint working")
            reply = response.json().get("reply", "")
            print(f"   📄 Response preview: {reply[:100]}...")
        else:
            print(f"   ❌ Chat endpoint failed: {response.status_code}")
            print(f"   📄 Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test multiple chat messages
    print("\n📋 Testing Multiple Messages...")
    test_messages = [
        "I need to buy groceries for healthy breakfast",
        "Schedule a meeting for tomorrow",
        "Help me plan my workout schedule"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n   Message {i}: {message}")
        chat_data = {
            "user_id": f"test_user_{i}",
            "message": message
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{base_url}/api/chat",
                json=chat_data,
                headers={"Content-Type": "application/json"}
            )
            end_time = time.time()
            
            if response.status_code == 200:
                reply = response.json().get("reply", "")
                print(f"      ✅ Success ({(end_time - start_time)*1000:.0f}ms)")
                print(f"      📄 Preview: {reply[:80]}...")
            else:
                print(f"      ❌ Failed: {response.status_code}")
        except Exception as e:
            print(f"      ❌ Error: {e}")
    
    print("\n✨ API testing completed!")
    return True

if __name__ == "__main__":
    test_api()
