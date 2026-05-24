#!/usr/bin/env python3
"""
Debug Authentication Process
Step by step debugging of OTP and login
"""

import requests
import sqlite3
from datetime import datetime

def check_database_user():
    """Check user in database"""
    try:
        conn = sqlite3.connect('hyperlocal_news.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT user_uid, phone, email, role FROM users WHERE phone = ?", ("8967452312",))
        user = cursor.fetchone()
        
        if user:
            print(f"✅ User in database:")
            print(f"   User UID: {user[0]}")
            print(f"   Phone: {user[1]}")
            print(f"   Email: {user[2]}")
            print(f"   Role: {user[3]}")
            return user
        else:
            print("❌ User not found in database")
            return None
            
    except Exception as e:
        print(f"❌ Error checking user: {e}")
        return None

def check_otp_table():
    """Check OTP table"""
    try:
        conn = sqlite3.connect('hyperlocal_news.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT phone, otp_code, expires_at, is_used FROM otp_tokens ORDER BY created_at DESC LIMIT 5")
        otp_records = cursor.fetchall()
        
        if otp_records:
            print(f"📱 Recent OTP records:")
            for record in otp_records:
                print(f"   Phone: {record[0]}, OTP: {record[1]}, Expires: {record[2]}, Used: {record[3]}")
        else:
            print("📱 No OTP records found")
            
    except Exception as e:
        print(f"❌ Error checking OTP: {e}")

def test_otp_send():
    """Test OTP sending"""
    base_url = "http://127.0.0.1:8000"
    
    try:
        response = requests.post(
            f"{base_url}/user/auth/send-otp",
            json={
                "type": "mobile",
                "value": "8967452312"
            },
            timeout=10
        )
        
        print(f"📱 OTP Send Response:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            otp = data.get('otp', 'N/A')
            print(f"   ✅ OTP Generated: {otp}")
            return otp
        else:
            print(f"   ❌ OTP Send Failed")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def test_login_with_otp(otp):
    """Test login with specific OTP"""
    base_url = "http://127.0.0.1:8000"
    
    try:
        response = requests.post(
            f"{base_url}/user/token/verify/login",
            json={
                "identifier": "8967452312",
                "otp": str(otp),
                "role": 4
            },
            timeout=10
        )
        
        print(f"🔐 Login Response:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            print(f"   ✅ Login Successful!")
            print(f"   Token: {token[:50]}..." if token else "No token")
            return token
        else:
            print(f"   ❌ Login Failed")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def test_different_identifiers():
    """Test login with different identifier formats"""
    base_url = "http://127.0.0.1:8000"
    identifiers = ["8967452312", "+8967452312", "USER8967"]
    
    for identifier in identifiers:
        print(f"\n🔍 Testing identifier: {identifier}")
        
        # Send OTP
        response = requests.post(
            f"{base_url}/user/auth/send-otp",
            json={
                "type": "mobile",
                "value": identifier
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            otp = data.get('otp', 'N/A')
            print(f"   OTP: {otp}")
            
            # Try login
            login_response = requests.post(
                f"{base_url}/user/token/verify/login",
                json={
                    "identifier": identifier,
                    "otp": str(otp),
                    "role": 4
                },
                timeout=10
            )
            
            print(f"   Login: {login_response.status_code}")
            if login_response.status_code == 200:
                print(f"   ✅ SUCCESS with {identifier}!")
                return True
        else:
            print(f"   OTP Send Failed: {response.status_code}")
    
    return False

def main():
    """Main debug function"""
    print("🔍 Debugging Authentication Process")
    print("=" * 50)
    
    # Check database
    check_database_user()
    
    # Check OTP table
    check_otp_table()
    
    print("\n" + "=" * 50)
    print("🧪 Testing Authentication Flow")
    print("=" * 50)
    
    # Test OTP send
    otp = test_otp_send()
    
    if otp:
        print("\n" + "=" * 30)
        # Test login with generated OTP
        test_login_with_otp(otp)
    
    print("\n" + "=" * 50)
    print("🔄 Testing Different Identifier Formats")
    print("=" * 50)
    
    # Test different formats
    test_different_identifiers()

if __name__ == "__main__":
    main()
