#!/usr/bin/env python3
"""
Start server and test rewards system
"""

import subprocess
import time
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting FastAPI Server...")
    
    try:
        # Start server in background
        process = subprocess.Popen([
            "python", "-m", "uvicorn", "main:app", "--port", "8000"
        ], 
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
        )
        
        print("✅ Server starting...")
        print("📡 Waiting for server to start...")
        
        # Wait for server to start
        time.sleep(5)
        
        print("🌐 Server should be running at: http://127.0.0.1:8000")
        print("📖 API Documentation: http://127.0.0.1:8000/docs")
        
        return process
        
    except Exception as e:
        print(f"❌ Error starting server: {str(e)}")
        return None

def test_rewards_system():
    """Test rewards system"""
    print("\n🎁 Testing Rewards System...")
    
    # Wait a bit for server to be ready
    time.sleep(2)
    
    # Send OTP
    otp_data = {
        "type": "email",
        "value": "test@example.com"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/user/auth/send-otp", json=otp_data, timeout=5)
        print(f"OTP Send: {response.status_code}")
        
        if response.status_code == 200:
            otp_response = response.json()
            otp_code = otp_response.get('otp', '123456')
            print(f"✅ OTP: {otp_code}")
            
            # Login
            login_data = {
                "identifier": "test@example.com",
                "role": 5,
                "otp": otp_code
            }
            
            response = requests.post(f"{BASE_URL}/user/token/verify-otp", json=login_data, timeout=5)
            print(f"Login: {response.status_code}")
            
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get("access_token")
                print(f"✅ Token: {access_token[:30]}...")
                
                # Test rewards endpoints
                test_rewards_endpoints(access_token)
            else:
                print(f"❌ Login failed: {response.text}")
        else:
            print(f"❌ OTP failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_rewards_endpoints(token):
    """Test key rewards endpoints"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("\n🎁 Testing Rewards Endpoints:")
    
    endpoints = [
        ("GET", "/rewards/wallet", "💰 Wallet"),
        ("GET", "/rewards/referral/info", "🔗 Referral"),
        ("GET", "/rewards/leaderboard", "🏆 Leaderboard"),
        ("POST", "/rewards/daily/login", "🎁 Daily Reward")
    ]
    
    working_count = 0
    
    for method, endpoint, description in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=5)
            else:
                response = requests.post(f"{BASE_URL}{endpoint}", headers=headers, timeout=5)
            
            print(f"{description}: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ Working")
                working_count += 1
            elif response.status_code == 401:
                print(f"❌ Not authenticated")
            else:
                print(f"❌ Error: {response.text}")
                
        except Exception as e:
            print(f"❌ {description} error: {str(e)}")
    
    print(f"\n📊 Results: {working_count}/{len(endpoints)} endpoints working")
    
    if working_count > 0:
        print("🎉 Rewards system is working!")
    else:
        print("❌ Rewards system needs attention")

def main():
    print("🚀 Start Server & Test Rewards")
    print("=" * 60)
    
    # Start server
    server_process = start_server()
    
    if server_process:
        # Test rewards system
        test_rewards_system()
        
        print("\n" + "=" * 60)
        print("💡 Server is running in background")
        print("🌐 Access at: http://127.0.0.1:8000")
        print("📖 API Docs: http://127.0.0.1:8000/docs")
        print("🛑 Press Ctrl+C to stop server")
        
        try:
            # Wait for user to stop
            server_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping server...")
            server_process.terminate()
    else:
        print("❌ Failed to start server")

if __name__ == "__main__":
    main()
