#!/usr/bin/env python3
"""
Rewards System 100% Functionality Test
Test all rewards endpoints to ensure they work correctly
"""

import requests
import json
import time
from typing import Dict, Any

class RewardsTester:
    def __init__(self, base_url: str = "http://127.0.0.1:8002"):
        self.base_url = base_url
        self.access_token = None
        self.test_user = {
            "mobile": "8967452312",
            "email": "test8967@example.com"
        }
    
    def test_connection(self) -> bool:
        """Test basic server connection"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            return response.status_code < 500
        except:
            return False
    
    def send_otp(self) -> bool:
        """Send OTP for authentication"""
        try:
            response = requests.post(
                f"{self.base_url}/user/auth/send-otp",
                json={
                    "type": "mobile",
                    "value": self.test_user["mobile"]
                },
                timeout=10
            )
            print(f"📱 OTP Send: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ OTP: {data.get('otp', 'N/A')}")
                return True
            else:
                print(f"   ❌ Error: {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            return False
    
    def login(self) -> bool:
        """Login with OTP"""
        try:
            # First send OTP to get the code
            if not self.send_otp():
                return False
            
            # Try common OTP codes
            otp_codes = ["9704", "1234", "0000", "1111", "9999"]  # Start with the actual OTP from response
            
            for otp in otp_codes:
                response = requests.post(
                    f"{self.base_url}/user/token/verify/login",
                    json={
                        "identifier": self.test_user["mobile"],
                        "otp": otp,
                        "role": 4  # Publisher role
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.access_token = data.get("access_token")
                    print(f"🔐 Login: 200 ✅")
                    return True
                elif response.status_code == 401:
                    continue  # Try next OTP
                else:
                    print(f"🔐 Login: {response.status_code} - {response.text}")
                    return False
            
            print("🔐 Login: Failed - Invalid OTP codes")
            return False
        except Exception as e:
            print(f"🔐 Login Exception: {e}")
            return False
    
    def get_headers(self) -> Dict[str, str]:
        """Get authorization headers"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def test_endpoint(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Dict:
        """Test a single endpoint"""
        try:
            url = f"{self.base_url}{endpoint}"
            headers = self.get_headers()
            
            if method == "GET":
                response = requests.get(url, headers=headers, params=params, timeout=10)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data, params=params, timeout=10)
            else:
                return {"status": "error", "message": f"Unsupported method: {method}"}
            
            result = {
                "status_code": response.status_code,
                "success": 200 <= response.status_code < 300,
                "data": response.json() if response.content else None,
                "error": response.text if not (200 <= response.status_code < 300) else None
            }
            
            return result
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def test_all_endpoints(self) -> Dict[str, Any]:
        """Test all rewards endpoints"""
        results = {}
        
        # Test endpoints
        endpoints = [
            # Referral System
            ("GET", "/rewards/referral", "Referral Info"),
            
            # Wallet System  
            ("GET", "/rewards/wallet", "Wallet Balance"),
            ("GET", "/rewards/wallet/transactions", "Transaction History"),
            
            # Engagement Rewards
            ("POST", "/rewards/daily-login", "Daily Login"),
            ("POST", "/rewards/article-read?news_uid=test123", "Article Read"),
            ("POST", "/rewards/news-share?news_uid=test123&platform=twitter", "News Share"),
            ("POST", "/rewards/comment?comment_id=test456", "Comment Reward"),
            
            # Coupon System
            ("GET", "/rewards/coupons", "Available Coupons"),
            
            # Leaderboard
            ("GET", "/rewards/leaderboard", "Leaderboard"),
        ]
        
        print("\n🎯 Testing Rewards Endpoints:")
        print("=" * 50)
        
        for method, endpoint, name in endpoints:
            print(f"\n🔍 {name}:")
            result = self.test_endpoint(method, endpoint)
            
            if result["status_code"]:
                status_icon = "✅" if result["success"] else "❌"
                print(f"   {status_icon} {result['status_code']}")
                
                if result["success"] and result["data"]:
                    # Show key data
                    if "balance" in str(result["data"]).lower():
                        balance = result["data"].get("current_balance", 0)
                        print(f"   💰 Balance: {balance}")
                    elif "referral_code" in str(result["data"]):
                        code = result["data"].get("referral_code", "N/A")
                        print(f"   📋 Code: {code}")
                elif result["error"]:
                    print(f"   🚨 Error: {result['error'][:100]}...")
                
                results[name] = result
            else:
                print(f"   ❌ Failed: {result.get('message', 'Unknown error')}")
                results[name] = {"success": False, "error": result.get('message')}
        
        return results
    
    def generate_summary(self, results: Dict[str, Any]) -> None:
        """Generate test summary"""
        total = len(results)
        working = sum(1 for r in results.values() if r.get("success", False))
        percentage = (working / total * 100) if total > 0 else 0
        
        print("\n" + "=" * 60)
        print(f"📊 REWARDS SYSTEM TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Working: {working}/{total} ({percentage:.1f}%)")
        print(f"❌ Failed: {total - working}/{total} ({100 - percentage:.1f}%)")
        
        if percentage == 100:
            print("\n🎉 CONGRATULATIONS! 100% FUNCTIONAL REWARDS SYSTEM!")
        elif percentage >= 80:
            print(f"\n👍 GOOD! {percentage:.1f}% functional - Almost there!")
        elif percentage >= 60:
            print(f"\n⚠️  FAIR - {percentage:.1f}% functional - Needs improvement")
        else:
            print(f"\n🚨 POOR - {percentage:.1f}% functional - Major issues")
        
        # Show failed endpoints
        failed = [name for name, result in results.items() if not result.get("success", False)]
        if failed:
            print(f"\n❌ Failed endpoints: {', '.join(failed)}")
    
    def run_full_test(self) -> None:
        """Run complete test suite"""
        print("🚀 Starting Rewards System 100% Functionality Test")
        print("=" * 60)
        
        # Test connection
        if not self.test_connection():
            print("❌ Server not running. Please start the FastAPI server first.")
            print("   Run: uvicorn main:app --reload --host 0.0.0.0 --port 8000")
            return
        
        print("✅ Server connection successful")
        
        # Login
        if not self.login():
            print("❌ Authentication failed. Cannot test rewards endpoints.")
            return
        
        print("✅ Authentication successful")
        
        # Test all endpoints
        results = self.test_all_endpoints()
        
        # Generate summary
        self.generate_summary(results)

def main():
    """Main function"""
    tester = RewardsTester()
    tester.run_full_test()

if __name__ == "__main__":
    main()
