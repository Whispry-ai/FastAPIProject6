#!/usr/bin/env python3
"""
Debug the login role mismatch issue
"""

import sqlite3
import requests

BASE_URL = "http://127.0.0.1:8002"
DB_PATH = "news_platform.db"

def debug_user_role():
    """Debug user role in database"""
    print("🔍 Debugging User Role Issue")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get user details
        cursor.execute("""
            SELECT user_uid, email, phone, name, role, created_at, is_active, email_verified, mobile_verified, token_version 
            FROM users 
            WHERE email = 'test@example.com'
        """)
        user = cursor.fetchone()
        
        if user:
            user_uid, email, phone, name, role, created_at, is_active, email_verified, mobile_verified, token_version = user
            print(f"User from database:")
            print(f"  Email: {email}")
            print(f"  Name: {name}")
            print(f"  Role (int): {role}")
            print(f"  Role (str): {str(role)}")
            print(f"  Role (type): {type(role)}")
            
            # Test login with different role formats
            print(f"\n🔐 Testing login with different role formats:")
            
            role_variations = [
                role,           # Direct from database
                str(role),      # String conversion
                int(role),       # Integer conversion
                1,              # Hardcoded USER role
                "1",            # String USER role
            ]
            
            for i, test_role in enumerate(role_variations):
                print(f"\nTest {i+1}: role = {test_role} (type: {type(test_role)})")
                
                # Send OTP
                otp_data = {
                    "type": "email",
                    "value": "test@example.com"
                }
                
                try:
                    otp_response = requests.post(f"{BASE_URL}/user/auth/send-otp", json=otp_data)
                    if otp_response.status_code == 200:
                        otp_data = otp_response.json()
                        otp_code = otp_data.get('otp', '123456')
                        
                        # Try login
                        login_data = {
                            "identifier": "test@example.com",
                            "role": test_role,
                            "otp": otp_code
                        }
                        
                        login_response = requests.post(f"{BASE_URL}/user/token/verify/login", json=login_data)
                        print(f"  Login: {login_response.status_code}")
                        
                        if login_response.status_code == 200:
                            print(f"  ✅ SUCCESS! Role {test_role} works")
                            token_data = login_response.json()
                            access_token = token_data.get("access_token")
                            test_rewards_with_token(access_token)
                            return
                        else:
                            print(f"  ❌ Failed: {login_response.text}")
                    else:
                        print(f"  ❌ OTP failed: {otp_response.text}")
                        
                except Exception as e:
                    print(f"  ❌ Error: {str(e)}")
        
        else:
            print("❌ User not found in database")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {str(e)}")

def test_rewards_with_token(token):
    """Test rewards endpoints"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"\n🎁 Testing Rewards with valid token...")
    
    try:
        response = requests.get(f"{BASE_URL}/rewards/wallet", headers=headers)
        print(f"Wallet: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ {response.json()}")
        else:
            print(f"❌ {response.text}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    debug_user_role()

if __name__ == "__main__":
    main()
