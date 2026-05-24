#!/usr/bin/env python3
"""
Auto start server and test rewards
"""

import subprocess
import time
import requests
import os
import signal

BASE_URL = "http://127.0.0.1:8000"

def start_server():
    """Start server"""
    print("🚀 Starting FastAPI Server...")
    
    try:
        # Start server
        process = subprocess.Popen([
            "python", "-m", "uvicorn", "main:app", "--port", "8000"
        ], 
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
        )
        
        print("✅ Server starting...")
        
        # Wait for server to be ready
        for i in range(15):
            try:
                response = requests.get(f"{BASE_URL}/", timeout=2)
                if response.status_code == 200:
                    print("✅ Server is ready!")
                    return process
            except:
                pass
            time.sleep(1)
            print(f"⏳ Waiting... {i+1}/15")
        
        print("❌ Server failed to start")
        return None
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def test_rewards():
    """Test rewards endpoints"""
    print("\n🎁 Testing Rewards System...")
    
    # Get token
    token = get_token()
    if not token:
        print("❌ Cannot get token")
        return
    
    # Test endpoints
    test_endpoints(token)

def get_token():
    """Get authentication token"""
    try:
        # Send OTP
        otp_data = {"type": "email", "value": "test@example.com"}
        response = requests.post(f"{BASE_URL}/user/auth/send-otp", json=otp_data, timeout=5)
        
        if response.status_code == 200:
            otp_response = response.json()
            otp_code = otp_response.get('otp', '123456')
            
            # Login
            login_data = {"identifier": "test@example.com", "role": 5, "otp": otp_code}
            response = requests.post(f"{BASE_URL}/user/token/verify-otp", json=login_data, timeout=5)
            
            if response.status_code == 200:
                token_data = response.json()
                return token_data.get("access_token")
        
        return None
        
    except Exception as e:
        print(f"❌ Token error: {str(e)}")
        return None

def test_endpoints(token):
    """Test rewards endpoints"""
    headers = {"Authorization": f"Bearer {token}"}
    
    endpoints = [
        ("GET", "/rewards/wallet", "💰 Wallet"),
        ("GET", "/rewards/referral/info", "🔗 Referral"),
        ("GET", "/rewards/leaderboard", "🏆 Leaderboard"),
        ("POST", "/rewards/daily/login", "🎁 Daily")
    ]
    
    print("\nTesting endpoints:")
    working = 0
    
    for method, endpoint, name in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=5)
            else:
                response = requests.post(f"{BASE_URL}{endpoint}", headers=headers, timeout=5)
            
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} {name}: {response.status_code}")
            
            if response.status_code == 200:
                working += 1
                
        except Exception as e:
            print(f"❌ {name}: Error")
    
    print(f"\n📊 Results: {working}/{len(endpoints)} working")
    
    if working > 0:
        print("🎉 Rewards system is working!")
    else:
        print("❌ Rewards system needs attention")

def main():
    print("🚀 Auto Start Server & Test Rewards")
    print("=" * 50)
    
    # Start server
    server_process = start_server()
    
    if server_process:
        try:
            # Test rewards
            test_rewards()
            
            print("\n" + "=" * 50)
            print("🌐 Server running at: http://127.0.0.1:8000")
            print("📖 API Docs: http://127.0.0.1:8000/docs")
            print("🛑 Press Ctrl+C to stop server")
            
            # Keep server running
            server_process.wait()
            
        except KeyboardInterrupt:
            print("\n🛑 Stopping server...")
            server_process.terminate()
    else:
        print("❌ Failed to start server")

if __name__ == "__main__":
    main()
