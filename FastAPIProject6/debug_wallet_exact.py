#!/usr/bin/env python3
"""
Debug and Fix Specific Wallet Error
Find the exact column causing the issue and fix it
"""

import psycopg2

def get_exact_wallet_error():
    """Get the exact wallet error details"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            user="postgres",
            password="password",
            database="news_platform"
        )
        cursor = conn.cursor()
        
        print("🔍 Getting Exact Wallet Error Details")
        print("=" * 50)
        
        # Test the exact query that's failing
        try:
            cursor.execute("""
                SELECT uw.user_uid, uw.current_balance, uw.total_earned, uw.total_spent, 
                       uw.daily_streak, uw.longest_streak, uw.created_at, uw.updated_at
                FROM user_wallets uw
                WHERE uw.user_uid = 'USER8967'
            """)
            
            result = cursor.fetchone()
            if result:
                print("✅ Direct wallet query works:")
                print(f"   User: {result[0]}")
                print(f"   Balance: {result[1]}")
                print(f"   Earned: {result[2]}")
            else:
                print("❌ No wallet found")
                
        except Exception as e:
            print(f"❌ Direct query error: {e}")
        
        # Check all columns in user_wallets table
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'user_wallets'
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        
        print(f"\n📋 All user_wallets columns ({len(columns)}):")
        for col in columns:
            nullable = "NULL" if col[2] == "YES" else "NOT NULL"
            print(f"   {col[0]} ({col[1]}) {nullable}")
        
        # Check if there are any unexpected columns
        unexpected_columns = [col[0] for col in columns if col[0] not in [
            'id', 'user_uid', 'current_balance', 'total_earned', 'total_spent',
            'daily_streak', 'longest_streak', 'created_at', 'updated_at'
        ]]
        
        if unexpected_columns:
            print(f"\n⚠️  Unexpected columns found: {unexpected_columns}")
        else:
            print(f"\n✅ All expected columns present")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def test_wallet_endpoint_with_debug():
    """Test wallet endpoint with detailed error capture"""
    try:
        import requests
        
        base_url = "http://127.0.0.1:8002"
        
        # Get authentication token first
        otp_response = requests.post(
            f"{base_url}/user/auth/send-otp",
            json={
                "type": "mobile",
                "value": "8967452312"
            },
            timeout=10
        )
        
        if otp_response.status_code != 200:
            print("❌ Failed to send OTP")
            return
        
        otp_data = otp_response.json()
        otp = otp_data.get('otp', 'N/A')
        
        login_response = requests.post(
            f"{base_url}/user/token/verify/login",
            json={
                "identifier": "8967452312",
                "otp": str(otp),
                "role": 4
            },
            timeout=10
        )
        
        if login_response.status_code != 200:
            print("❌ Failed to login")
            return
        
        token_data = login_response.json()
        access_token = token_data.get('access_token')
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        print(f"\n💰 Testing Wallet Balance endpoint...")
        wallet_response = requests.get(
            f"{base_url}/rewards/wallet",
            headers=headers,
            timeout=10
        )
        
        print(f"Status: {wallet_response.status_code}")
        
        if wallet_response.status_code == 500:
            error_text = wallet_response.text
            print(f"Error: {error_text}")
            
            # Extract the specific column name from error
            if "UndefinedColumn" in error_text:
                import re
                match = re.search(r'column "([^"]+)"', error_text)
                if match:
                    column_name = match.group(1)
                    print(f"🔍 Missing column: {column_name}")
                    
                    # Check if this column exists in database
                    conn = psycopg2.connect(
                        host="localhost",
                        port="5432",
                        user="postgres",
                        password="password",
                        database="news_platform"
                    )
                    cursor = conn.cursor()
                    
                    cursor.execute("""
                        SELECT column_name FROM information_schema.columns 
                        WHERE table_name = 'user_wallets' AND column_name = %s
                    """, (column_name,))
                    
                    if cursor.fetchone():
                        print(f"✅ Column {column_name} exists in database")
                    else:
                        print(f"❌ Column {column_name} does NOT exist in database")
                    
                    conn.close()
        else:
            print("✅ Wallet endpoint working!")
            
    except Exception as e:
        print(f"❌ Error testing wallet: {e}")

def main():
    """Main function"""
    get_exact_wallet_error()
    test_wallet_endpoint_with_debug()

if __name__ == "__main__":
    main()
