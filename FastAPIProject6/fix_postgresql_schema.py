#!/usr/bin/env python3
"""
Fix PostgreSQL Database Schema
Update user_wallets table to fix missing columns
"""

import psycopg2

def fix_wallets_table():
    """Fix user_wallets table schema"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            user="postgres",
            password="password",
            database="news_platform"
        )
        cursor = conn.cursor()
        
        print("🔧 Fixing PostgreSQL Database Schema")
        print("=" * 50)
        
        # Check current table structure
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'user_wallets' 
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        
        print("📋 Current user_wallets columns:")
        for col in columns:
            print(f"   {col[0]} ({col[1]})")
        
        # Add missing columns if they don't exist
        columns_to_add = [
            ("created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
            ("updated_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        ]
        
        for col_name, col_def in columns_to_add:
            # Check if column exists
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'user_wallets' AND column_name = %s
            """, (col_name,))
            
            if not cursor.fetchone():
                print(f"➕ Adding column: {col_name}")
                cursor.execute(f"""
                    ALTER TABLE user_wallets 
                    ADD COLUMN {col_name} {col_def}
                """)
            else:
                print(f"✅ Column {col_name} already exists")
        
        conn.commit()
        print("✅ Database schema fixed")
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error fixing database: {e}")
        return False

def check_transaction_history_endpoint():
    """Check if transaction history endpoint exists"""
    try:
        import requests
        
        # Get authentication token first
        base_url = "http://127.0.0.1:8001"
        
        otp_response = requests.post(
            f"{base_url}/user/auth/send-otp",
            json={
                "type": "mobile",
                "value": "8967452312"
            },
            timeout=10
        )
        
        if otp_response.status_code != 200:
            print("❌ Failed to get OTP")
            return False
        
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
            return False
        
        token_data = login_response.json()
        access_token = token_data.get('access_token')
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Test transaction history endpoint
        response = requests.get(
            f"{base_url}/rewards/wallet/transactions",
            headers=headers,
            timeout=10
        )
        
        print(f"📊 Transaction History endpoint: {response.status_code}")
        
        if response.status_code == 404:
            print("❌ Endpoint not found - checking routes...")
            
            # Check if endpoint is registered in main.py
            try:
                with open('main.py', 'r') as f:
                    main_content = f.read()
                
                if 'rewards' in main_content and 'wallet' in main_content:
                    print("✅ Rewards router is included in main")
                else:
                    print("❌ Rewards router might not be properly included")
                
                if 'wallet/transactions' in main_content:
                    print("✅ Transaction history route exists")
                else:
                    print("❌ Transaction history route missing")
                    
            except Exception as e:
                print(f"❌ Error checking main.py: {e}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Error testing endpoint: {e}")
        return False

def main():
    """Main function"""
    if fix_wallets_table():
        check_transaction_history_endpoint()

if __name__ == "__main__":
    main()
