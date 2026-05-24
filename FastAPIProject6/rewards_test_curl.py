#!/usr/bin/env python3
"""
Generate curl commands for rewards testing
"""

BASE_URL = "http://127.0.0.1:8000"

def generate_curl_commands():
    """Generate curl commands for testing"""
    print("🎁 Rewards System - Curl Commands")
    print("=" * 50)
    
    print("\n📱 Step 1: Send OTP")
    print("curl -X 'POST' \\")
    print(f"  '{BASE_URL}/user/auth/send-otp' \\")
    print("  -H 'accept: application/json' \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{")
    print("    \"type\": \"email\",")
    print("    \"value\": \"test@example.com\"")
    print("  }'")
    
    print("\n🔐 Step 2: Login (Replace OTP_CODE)")
    print("curl -X 'POST' \\")
    print(f"  '{BASE_URL}/user/token/verify-otp' \\")
    print("  -H 'accept: application/json' \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{")
    print("    \"identifier\": \"test@example.com\",")
    print("    \"role\": 5,")
    print("    \"otp\": \"OTP_CODE_HERE\"")
    print("  }'")
    
    print("\n🎁 Step 3: Test Rewards (Replace TOKEN)")
    print("curl -X 'GET' \\")
    print(f"  '{BASE_URL}/rewards/wallet' \\")
    print("  -H 'accept: application/json' \\")
    print("  -H 'Authorization: Bearer ACCESS_TOKEN_HERE'")
    
    print("\n🔗 Referral Info")
    print("curl -X 'GET' \\")
    print(f"  '{BASE_URL}/rewards/referral/info' \\")
    print("  -H 'accept: application/json' \\")
    print("  -H 'Authorization: Bearer ACCESS_TOKEN_HERE'")
    
    print("\n🏆 Leaderboard")
    print("curl -X 'GET' \\")
    print(f"  '{BASE_URL}/rewards/leaderboard' \\")
    print("  -H 'accept: application/json' \\")
    print("  -H 'Authorization: Bearer ACCESS_TOKEN_HERE'")
    
    print("\n🎁 Daily Reward")
    print("curl -X 'POST' \\")
    print(f"  '{BASE_URL}/rewards/daily/login' \\")
    print("  -H 'accept: application/json' \\")
    print("  -H 'Authorization: Bearer ACCESS_TOKEN_HERE'")
    
    print("\n📊 Transaction History")
    print("curl -X 'GET' \\")
    print(f"  '{BASE_URL}/rewards/transactions/history' \\")
    print("  -H 'accept: application/json' \\")
    print("  -H 'Authorization: Bearer ACCESS_TOKEN_HERE'")
    
    print("\n" + "=" * 50)
    print("💡 Instructions:")
    print("1. Run Step 1 to get OTP")
    print("2. Replace OTP_CODE_HERE in Step 2")
    print("3. Run Step 2 to get access token")
    print("4. Replace ACCESS_TOKEN_HERE in Step 3")
    print("5. Run Step 3 commands to test rewards")

if __name__ == "__main__":
    generate_curl_commands()
