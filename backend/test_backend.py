#!/usr/bin/env python3
"""
Test script for LifePilot backend
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.agents.router import RouterAgent

async def test_backend():
    """Test the backend agent pipeline"""
    print("🧪 Testing LifePilot Backend...")
    
    # Initialize router agent
    router = RouterAgent()
    
    # Test cases
    test_cases = [
        {
            "user_id": "test_user_1",
            "message": "Plan my morning routine",
            "description": "Morning routine planning"
        },
        {
            "user_id": "test_user_2", 
            "message": "I need to buy groceries for healthy breakfast",
            "description": "Shopping with product recommendations"
        },
        {
            "user_id": "test_user_3",
            "message": "Schedule a meeting for tomorrow",
            "description": "Calendar integration"
        },
        {
            "user_id": "test_user_4",
            "message": "Help me plan my workout schedule",
            "description": "General planning"
        }
    ]
    
    # Run tests
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['description']}")
        print(f"   User: {test_case['user_id']}")
        print(f"   Message: {test_case['message']}")
        print("   Processing...")
        
        try:
            response = await router.process_message(
                user_id=test_case['user_id'],
                message=test_case['message']
            )
            
            print(f"   ✅ Success!")
            print(f"   📄 Response preview: {response[:100]}...")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print("\n🎉 Backend testing completed!")
    
    # Test session service
    print("\n🔧 Testing Session Service...")
    session_id = router.session_service.create_session("test_user")
    session = router.session_service.get_session(session_id)
    
    if session:
        print(f"   ✅ Session created: {session_id[:20]}...")
        print(f"   📊 Message count: {session['message_count']}")
    else:
        print("   ❌ Session creation failed")
    
    # Test memory bank
    print("\n💾 Testing Memory Bank...")
    success = router.memory_bank.store_memory("test_user", "test_key", "test_value", "test_category")
    if success:
        value = router.memory_bank.get_memory("test_user", "test_key")
        if value == "test_value":
            print("   ✅ Memory storage and retrieval working")
        else:
            print("   ❌ Memory retrieval failed")
    else:
        print("   ❌ Memory storage failed")
    
    # Test tools
    print("\n🛠️  Testing Tools...")
    
    # Test web search
    search_results = router.web_search_tool.search("morning routine")
    print(f"   🔍 Web search found {len(search_results)} results")
    
    # Test calendar
    from datetime import datetime, timedelta
    tomorrow = datetime.now() + timedelta(days=1)
    events = router.calendar_tool.get_events_for_date(tomorrow)
    print(f"   📅 Calendar found {len(events)} events for tomorrow")
    
    # Test shopping
    products = router.shopping_tool.search_products("oats")
    print(f"   🛒 Shopping found {len(products)} products")
    
    print("\n✨ All tests completed!")

if __name__ == "__main__":
    asyncio.run(test_backend())
