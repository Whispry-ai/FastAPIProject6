#!/usr/bin/env python3
"""
Test Authentication with Different Formats
Test various phone number formats to find the working one
"""

import requests
import psycopg2

def test_phone_formats():
    """Test different phone number formats"""
    base_url = "http://127.0.0.1:8000"
    
    # Different formats to test
    phone_formats = [
        "8967452312",           # Plain
        "+8967452312",          # With plus
        "008967452312",         # With international prefix
        "918967452312",         # With India code
        "+918967452312",        # With India code and plus
    ]
    
    print("🧪 Testing Different Phone Formats")
    print("=" * 50)
    
    for phone in phone_formats:
        print(f"\n📱 Testing format: '{phone}'")
        
        # Send OTP
        try:
            otp_response = requests.post(
                f"{base_url}/user/auth/send-otp",
                json={
                    "type": "mobile",
                    "value": phone
                },
                timeout=10
            )
            
            print(f"   OTP Send: {otp_response.status_code}")
            
            if otp_response.status_code == 200:
                otp_data = otp_response.json()
                otp = otp_data.get('otp', 'N/A')
                print(f"   OTP: {otp}")
                
                # Try login
                login_response = requests.post(
                    f"{base_url}/user/token/verify/login",
                    json={
                        "identifier": phone,
                        "otp": str(otp),
                        "role": 4
                    },
                    timeout=10
                )
                
                print(f"   Login: {login_response.status_code}")
                
                if login_response.status_code == 200:
                    token_data = login_response.json()
                    access_token = token_data.get('access_token')
                    print(f"   ✅ SUCCESS! Token: {access_token[:50]}...")
                    return access_token
                else:
                    print(f"   ❌ Login failed: {login_response.text}")
            else:
                print(f"   ❌ OTP failed: {otp_response.text}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    return None

def check_database_phone_formats():
    """Check what phone formats exist in database"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            user="postgres",
            password="password",
            database="news_platform"
        )
        cursor = conn.cursor()
        
        print("📋 Phone formats in database:")
        cursor.execute("SELECT user_uid, phone FROM users")
        users = cursor.fetchall()
        
        for user in users:
            print(f"   UID: {user[0]}, Phone: '{user[1]}'")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def test_email_login():
    """Test login with email instead of phone"""
    base_url = "http://127.0.0.1:8000"
    email = "test8967@example.com"
    
    print(f"\n📧 Testing email login: '{email}'")
    
    try:
        # Send OTP with email
        otp_response = requests.post(
            f"{base_url}/user/auth/send-otp",
            json={
                "type": "email",
                "value": email
            },
            timeout=10
        )
        
        print(f"   OTP Send: {otp_response.status_code}")
        
        if otp_response.status_code == 200:
            otp_data = otp_response.json()
            otp = otp_data.get('otp', 'N/A')
            print(f"   OTP: {otp}")
            
            # Try login with email
            login_response = requests.post(
                f"{base_url}/user/token/verify/login",
                json={
                    "identifier": email,
                    "otp": str(otp),
                    "role": 4
                },
                timeout=10
            )
            
            print(f"   Login: {login_response.status_code}")
            
            if login_response.status_code == 200:
                token_data = login_response.json()
                access_token = token_data.get('access_token')
                print(f"   ✅ SUCCESS! Token: {access_token[:50]}...")
                return access_token
            else:
                print(f"   ❌ Login failed: {login_response.text}")
        else:
            print(f"   ❌ OTP failed: {otp_response.text}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    return None

def main():
    """Main function"""
    check_database_phone_formats()
    
    # Test phone formats
    token = test_phone_formats()
    
    if not token:
        # Test email login
        token = test_email_login()
    
    if token:
        print(f"\n🎉 Authentication successful!")
        print("   Ready to test rewards endpoints for 100% functionality")
    else:
        print(f"\n❌ All authentication attempts failed")

if __name__ == "__main__":
    main()
