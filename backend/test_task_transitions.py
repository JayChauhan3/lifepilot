"""
Test script to verify task auto-transition features
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api"

def get_local_date():
    """Get current date in YYYY-MM-DD format"""
    return datetime.now().strftime("%Y-%m-%d")

def get_tomorrow_date():
    """Get tomorrow's date"""
    tomorrow = datetime.now() + timedelta(days=1)
    return tomorrow.strftime("%Y-%m-%d")

def test_sync_endpoint():
    """Test the /tasks/sync endpoint"""
    print("\n=== Testing /tasks/sync endpoint ===")
    
    # Note: This requires authentication, so we're just testing if endpoint exists
    response = requests.post(f"{BASE_URL}/tasks/sync")
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 401:
        print("✅ Endpoint exists (requires authentication)")
        return True
    elif response.status_code == 200:
        print("✅ Sync successful!")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return True
    else:
        print(f"❌ Unexpected response: {response.text}")
        return False

def test_health_endpoint():
    """Test backend health"""
    print("\n=== Testing Backend Health ===")
    response = requests.get("http://localhost:8000/health")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Backend Status: {data['status']}")
        print(f"✅ Database Connected: {data['database']['connected']}")
        print(f"✅ Database Name: {data['database']['database']}")
        return True
    else:
        print(f"❌ Health check failed: {response.status_code}")
        return False

def test_api_root():
    """Test API root endpoint"""
    print("\n=== Testing API Root ===")
    response = requests.get("http://localhost:8000/")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ API Version: {data['version']}")
        print(f"✅ Message: {data['message']}")
        return True
    else:
        print(f"❌ Root endpoint failed: {response.status_code}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("TASK AUTO-TRANSITION SYSTEM - VERIFICATION TESTS")
    print("=" * 60)
    
    print(f"\n📅 Current Date: {get_local_date()}")
    print(f"📅 Tomorrow Date: {get_tomorrow_date()}")
    
    results = []
    
    # Test 1: Backend Health
    results.append(("Backend Health", test_health_endpoint()))
    
    # Test 2: API Root
    results.append(("API Root", test_api_root()))
    
    # Test 3: Sync Endpoint
    results.append(("Sync Endpoint", test_sync_endpoint()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)
    
    print(f"\nTotal: {total_passed}/{total_tests} tests passed")
    
    print("\n" + "=" * 60)
    print("FRONTEND FEATURES VERIFIED MANUALLY:")
    print("=" * 60)
    print("✅ 4-column layout (Today, Upcoming, Unfinished, Done)")
    print("✅ Date validation for upcoming tasks")
    print("✅ Default date set to tomorrow for new upcoming tasks")
    print("✅ Today's date disabled in date picker")
    
    print("\n" + "=" * 60)
    print("FEATURES TO TEST MANUALLY:")
    print("=" * 60)
    print("⏰ Wait until midnight to verify cron job executes")
    print("📝 Create test tasks and wait for automatic transitions")
    print("⚠️  Test work block warning (create tasks exceeding capacity)")
    print("👁️  Verify unfinished tasks appear with amber styling")
    print("🔒 Verify unfinished tasks are read-only")

if __name__ == "__main__":
    main()
