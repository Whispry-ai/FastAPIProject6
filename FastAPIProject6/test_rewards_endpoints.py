#!/usr/bin/env python3
"""
Test Rewards Endpoints
Simple test to verify rewards system is working
"""

import requests

BASE_URL = "http://localhost:8001"

def test_rewards_endpoints():
    """Test all rewards endpoints"""
    print("Testing Rewards Endpoints")
    print("=" * 40)
    
    # Test endpoints without auth (should return 401)
    endpoints = [
        "/rewards/referral",
        "/rewards/wallet", 
        "/rewards/coupons",
        "/rewards/leaderboard"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            if response.status_code == 401:
                print(f"✅ {endpoint}: Protected (401) - Working!")
            else:
                print(f"❌ {endpoint}: {response.status_code}")
        except:
            print(f"❌ {endpoint}: Error")
    
    print("\nNext Steps:")
    print("1. Login to get JWT token")
    print("2. Add Authorization header")
    print("3. Test with authentication")
    print(f"4. Open {BASE_URL}/docs for full testing")

if __name__ == "__main__":
    test_rewards_endpoints()