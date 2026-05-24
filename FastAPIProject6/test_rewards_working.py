#!/usr/bin/env python3
"""
Test Working Rewards System
Quick test to verify rewards system is working
"""

import requests
import json

BASE_URL = "http://localhost:8002"

def test_rewards_system():
    """Test the working rewards system"""
    print("🎯 **Testing Working Rewards System**")
    print("=" * 50)
    
    # Test server connection
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Server is running!")
        else:
            print(f"❌ Server error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return False
    
    # Test rewards endpoints
    endpoints = [
        ("Referral Info", "/rewards/referral"),
        ("Wallet Balance", "/rewards/wallet"),
        ("Daily Login", "/rewards/daily-login"),
        ("Article Read", "/rewards/article-read"),
        ("News Share", "/rewards/news-share"),
        ("Comment Reward", "/rewards/comment"),
        ("Available Coupons", "/rewards/coupons"),
        ("Leaderboard", "/rewards/leaderboard"),
    ]
    
    working_endpoints = 0
    for name, endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            if response.status_code == 200:
                working_endpoints += 1
                print(f"✅ {name}: Working (200)")
            elif response.status_code == 422:
                print(f"⚠️ {name}: Requires auth (422) - Expected!")
            else:
                print(f"❌ {name}: Error {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: Connection error")
    
    print(f"\n📊 **Results:**")
    print(f"   Working endpoints: {working_endpoints}/{len(endpoints)}")
    print(f"   Success rate: {(working_endpoints/len(endpoints)*100):.1f}%")
    
    if working_endpoints >= 6:
        print(f"\n🎉 **SUCCESS!** Rewards system is working!")
        print(f"\n🌐 **Access your rewards system:**")
        print(f"   📚 API Docs: {BASE_URL}/docs")
        print(f"   🎯 Referral: {BASE_URL}/rewards/referral")
        print(f"   💰 Wallet: {BASE_URL}/rewards/wallet")
        print(f"   🎁 Coupons: {BASE_URL}/rewards/coupons")
        print(f"   🏆 Leaderboard: {BASE_URL}/rewards/leaderboard")
        print(f"\n💡 **Next Steps:**")
        print("   1. Test with authentication (login first)")
        print("   2. Integrate with your main application")
        print("   3. Add referral codes to user signup")
        print("   4. Create reward notifications")
    else:
        print(f"\n⚠️ **PARTIAL SUCCESS:** {working_endpoints}/{len(endpoints)} endpoints working")
        print("   Check server logs for any errors")
        print("   Try restarting the simple rewards app")
    
    return working_endpoints >= 6

if __name__ == "__main__":
    success = test_rewards_system()
    if success:
        print("\n🚀 **Your rewards system is ready for integration!**")
    else:
        print("\n🔧 **Troubleshooting needed**")
