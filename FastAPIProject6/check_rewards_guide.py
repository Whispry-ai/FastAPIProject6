#!/usr/bin/env python3
"""
How to Check Rewards System
Multiple ways to verify your rewards system is working
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def check_rewards_methods():
    """Show different ways to check rewards system"""
    print("🔍 **How to Check Rewards System**")
    print("=" * 50)
    
    print("\n🌐 **Method 1: API Documentation (Recommended)**")
    print(f"   1. Open: {BASE_URL}/docs")
    print("   2. Look for 'Rewards' section")
    print("   3. Test endpoints with authentication")
    print("   4. Use 'Try it out' feature")
    
    print("\n📝 **Method 2: Direct API Testing**")
    print("   Run: python check_rewards_endpoints.py")
    print("   Tests all rewards endpoints with proper authentication")
    
    print("\n🔧 **Method 3: Database Check**")
    print("   1. Open pgAdmin")
    print("   2. Connect to news_platform.db")
    print("   3. Check these tables exist:")
    print("      • user_referrals")
    print("      • user_wallets")
    print("      • wallet_transactions")
    print("      • coupons")
    print("      • coupon_redemptions")
    print("      • daily_engagement")
    print("      • reward_settings")
    print("      • fraud_detection")
    print("      • leaderboard")
    
    print("\n📊 **Method 4: Frontend Testing**")
    print("   1. Open: {BASE_URL}/ai_analysis_client.html")
    print("   2. Check if rewards features appear")
    print("   3. Test referral generation")
    print("   4. Test wallet balance")
    
    print("\n🎯 **Key Rewards Endpoints to Test:**")
    print("   • GET /rewards/referral - Get referral code and stats")
    print("   • GET /rewards/wallet - Check wallet balance")
    print("   • POST /rewards/daily-login - Claim daily reward")
    print("   • POST /rewards/article-read - Claim reading reward")
    print("   • POST /rewards/news-share - Claim sharing reward")
    print("   • GET /rewards/coupons - View available coupons")
    print("   • GET /rewards/leaderboard - View rankings")
    
    print("\n🔐 **Authentication Required:**")
    print("   • Most rewards endpoints need user authentication")
    print("   • Admin endpoints need admin role")
    print("   • Use JWT token from login")
    
    print("\n⚡ **Quick Test Script:**")
    print("   python test_rewards_endpoints.py")

def create_quick_test():
    """Create quick test for rewards endpoints"""
    script = """#!/usr/bin/env python3
import requests

BASE_URL = "http://localhost:8001"

print("🎯 **Testing Rewards Endpoints**")
print("=" * 40)

# Test without auth (should return 401)
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

print("\\n📝 **Next Steps:**")
print("1. Login to get JWT token")
print("2. Add Authorization header")
print("3. Test with authentication")
print(f"4. Open {BASE_URL}/docs for full testing")
"""
    
    with open("test_rewards_endpoints.py", "w") as f:
        f.write(script)
    
    print("✅ Created: test_rewards_endpoints.py")

if __name__ == "__main__":
    check_rewards_methods()
    create_quick_test()
    
    print("\n🚀 **Choose Your Method:**")
    print("   🌐 API Docs: {BASE_URL}/docs")
    print("   📝 Quick Test: python test_rewards_endpoints.py")
    print("   🔧 Database: pgAdmin → news_platform.db")
