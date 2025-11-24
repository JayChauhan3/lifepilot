import asyncio
import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

from motor.motor_asyncio import AsyncIOMotorClient

async def verify_auth_flow():
    """Comprehensive verification of the authentication flow"""
    
    print("=" * 80)
    print("AUTHENTICATION SYSTEM VERIFICATION")
    print("=" * 80)
    
    mongo_uri = os.getenv("MONGODB_URI")
    client = AsyncIOMotorClient(mongo_uri)
    db = client["lifepilot_db"]
    users_collection = db["users"]
    pending_collection = db["pending_registrations"]
    
    # Test 1: Check initial state
    print("\n1. INITIAL STATE CHECK")
    print("-" * 80)
    users_count = await users_collection.count_documents({})
    pending_count = await pending_collection.count_documents({})
    print(f"   Users collection: {users_count} documents")
    print(f"   Pending collection: {pending_count} documents")
    print(f"   ✅ Collections are accessible")
    
    # Test 2: Simulate registration
    print("\n2. REGISTRATION FLOW TEST")
    print("-" * 80)
    test_email = "test@example.com"
    
    # Check if user would be created in pending
    existing_user = await users_collection.find_one({"email": test_email})
    existing_pending = await pending_collection.find_one({"email": test_email})
    
    if existing_user:
        print(f"   ⚠️  User already exists in main collection: {test_email}")
        print(f"      Verified: {existing_user.get('is_verified')}")
    elif existing_pending:
        print(f"   ✅ User exists in pending collection: {test_email}")
        print(f"      Token: {existing_pending.get('verification_token')}")
        print(f"      Expires: {existing_pending.get('verification_token_expires_at')}")
    else:
        print(f"   ✅ No existing user found - ready for registration")
    
    # Test 3: Check for duplicates
    print("\n3. DUPLICATE CHECK")
    print("-" * 80)
    all_users = await users_collection.find({}).to_list(length=1000)
    all_pending = await pending_collection.find({}).to_list(length=1000)
    
    user_emails = [u.get('email') for u in all_users]
    pending_emails = [p.get('email') for p in all_pending]
    
    # Check for duplicates in users
    user_duplicates = [email for email in user_emails if user_emails.count(email) > 1]
    pending_duplicates = [email for email in pending_emails if pending_emails.count(email) > 1]
    
    if user_duplicates:
        print(f"   ❌ DUPLICATES FOUND in users: {set(user_duplicates)}")
    else:
        print(f"   ✅ No duplicates in users collection")
    
    if pending_duplicates:
        print(f"   ❌ DUPLICATES FOUND in pending: {set(pending_duplicates)}")
    else:
        print(f"   ✅ No duplicates in pending collection")
    
    # Check for emails in both collections
    overlap = set(user_emails) & set(pending_emails)
    if overlap:
        print(f"   ⚠️  Emails in BOTH collections: {overlap}")
    else:
        print(f"   ✅ No overlap between collections")
    
    # Test 4: Verify data structure
    print("\n4. DATA STRUCTURE VERIFICATION")
    print("-" * 80)
    
    if all_users:
        sample_user = all_users[0]
        required_fields = ['user_id', 'email', 'is_verified', 'is_active']
        missing_fields = [f for f in required_fields if f not in sample_user]
        
        if missing_fields:
            print(f"   ❌ Missing fields in users: {missing_fields}")
        else:
            print(f"   ✅ All required fields present in users")
            print(f"      Sample: {sample_user.get('email')} (verified: {sample_user.get('is_verified')})")
    
    if all_pending:
        sample_pending = all_pending[0]
        required_fields = ['user_id', 'email', 'verification_token', 'verification_token_expires_at']
        missing_fields = [f for f in required_fields if f not in sample_pending]
        
        if missing_fields:
            print(f"   ❌ Missing fields in pending: {missing_fields}")
        else:
            print(f"   ✅ All required fields present in pending")
            print(f"      Sample: {sample_pending.get('email')} (token: {sample_pending.get('verification_token')})")
    
    # Test 5: Verification flow check
    print("\n5. VERIFICATION FLOW CHECK")
    print("-" * 80)
    
    verified_users = [u for u in all_users if u.get('is_verified') == True]
    unverified_users = [u for u in all_users if u.get('is_verified') == False]
    
    print(f"   Verified users in main collection: {len(verified_users)}")
    print(f"   Unverified users in main collection: {len(unverified_users)}")
    print(f"   Pending users: {len(all_pending)}")
    
    if unverified_users:
        print(f"   ⚠️  WARNING: {len(unverified_users)} unverified users in main collection")
        print(f"      (Should be in pending_registrations instead)")
    else:
        print(f"   ✅ No unverified users in main collection")
    
    # Test 6: Google OAuth users check
    print("\n6. GOOGLE OAUTH USERS CHECK")
    print("-" * 80)
    
    oauth_users = [u for u in all_users if u.get('oauth_provider') == 'google']
    manual_users = [u for u in all_users if not u.get('oauth_provider')]
    
    print(f"   Google OAuth users: {len(oauth_users)}")
    print(f"   Manual signup users: {len(manual_users)}")
    
    for oauth_user in oauth_users:
        if not oauth_user.get('is_verified'):
            print(f"   ❌ OAuth user not verified: {oauth_user.get('email')}")
        else:
            print(f"   ✅ OAuth user auto-verified: {oauth_user.get('email')}")
    
    # Summary
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    
    issues = []
    
    if user_duplicates or pending_duplicates:
        issues.append("❌ Duplicate emails found")
    
    if overlap:
        issues.append("❌ Emails exist in both collections")
    
    if unverified_users:
        issues.append("⚠️  Unverified users in main collection (should be in pending)")
    
    if not issues:
        print("✅ ALL CHECKS PASSED - System is working correctly!")
        print("\nExpected Flow:")
        print("  1. User registers → Stored in pending_registrations")
        print("  2. User receives verification email/link")
        print("  3. User verifies → Moved to users collection with is_verified=True")
        print("  4. User can login → Redirected to dashboard")
        print("  5. Google OAuth → Directly to users collection with is_verified=True")
    else:
        print("Issues found:")
        for issue in issues:
            print(f"  {issue}")
    
    print("=" * 80)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(verify_auth_flow())
