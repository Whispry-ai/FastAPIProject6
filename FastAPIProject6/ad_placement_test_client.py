#!/usr/bin/env python3
"""
Interactive Ad Placement Testing Client
Test and visualize ad placement with targeting
"""

import requests
import json
from datetime import datetime
from typing import Dict, Any, List

BASE_URL = "http://localhost:8001"

class AdPlacementTester:
    """Interactive ad placement testing client"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
    
    def test_connection(self) -> bool:
        """Test API connection"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_ad_config(self) -> Dict[str, Any]:
        """Get ad placement configuration"""
        try:
            response = self.session.get(f"{self.base_url}/ads/config")
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as e:
            print(f"Error getting config: {e}")
            return {}
    
    def test_ad_placement(self, user_uid: str, news_count: int = 20) -> Dict[str, Any]:
        """Test ad placement for specific user"""
        try:
            payload = {
                "user_uid": user_uid,
                "news_count": news_count,
                "placement_interval": 3,
                "max_ads": 5
            }
            
            response = self.session.post(
                f"{self.base_url}/ads/placement-test",
                json=payload
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return {}
        except Exception as e:
            print(f"Error testing placement: {e}")
            return {}
    
    def get_targeted_ads(self, token: str) -> Dict[str, Any]:
        """Get targeted ads for authenticated user"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = self.session.get(
                f"{self.base_url}/ads/targeted",
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error getting targeted ads: {response.status_code}")
                return {}
        except Exception as e:
            print(f"Error: {e}")
            return {}
    
    def get_ad_analytics(self, ad_id: int, token: str) -> Dict[str, Any]:
        """Get performance analytics for specific ad"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = self.session.get(
                f"{self.base_url}/ads/performance/{ad_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error getting analytics: {response.status_code}")
                return {}
        except Exception as e:
            print(f"Error: {e}")
            return {}
    
    def display_config(self, config: Dict[str, Any]):
        """Display ad placement configuration"""
        print("\n🔧 **Ad Placement Configuration**")
        print("=" * 50)
        
        if not config:
            print("❌ No configuration available")
            return
        
        cfg = config.get("config", {})
        logic = config.get("placement_logic", {})
        
        print(f"📊 Default Placement Interval: {cfg.get('default_placement_interval')}")
        print(f"📈 Max Ads per Feed: {cfg.get('max_ads_per_feed')}")
        print(f"🎯 Ad Types: {list(cfg.get('ad_types', {}).keys())}")
        
        print(f"\n📋 Placement Logic:")
        print(f"   {logic.get('description', 'N/A')}")
        print(f"   Example: {logic.get('example', 'N/A')}")
        print(f"   Max Protection: {logic.get('max_protection', 'N/A')}")
        print(f"   Smart Targeting: {logic.get('smart_targeting', 'N/A')}")
    
    def display_placement_results(self, results: Dict[str, Any]):
        """Display ad placement test results"""
        print("\n🎯 **Ad Placement Test Results**")
        print("=" * 50)
        
        if not results:
            print("❌ No results available")
            return
        
        # Test user info
        test_user = results.get("test_user", {})
        print(f"👤 Test User: {test_user.get('name', 'Unknown')}")
        print(f"   UID: {test_user.get('user_uid', 'N/A')}")
        
        # Location info
        location = test_user.get("location", {})
        print(f"📍 Location: State={location.get('state_id')}, District={location.get('district_id')}, City={location.get('city_id')}")
        
        # Demographics
        demographics = test_user.get("demographics", {})
        print(f"👥 Demographics: Gender={demographics.get('gender')}, Age={demographics.get('age')}")
        
        # Placement config
        placement_cfg = results.get("placement_config", {})
        print(f"\n⚙️  Placement Config:")
        print(f"   Interval: Every {placement_cfg.get('placement_interval')} articles")
        print(f"   Max Ads: {placement_cfg.get('max_ads')} per feed")
        
        # Results summary
        results_summary = results.get("results", {})
        print(f"\n📊 Results Summary:")
        print(f"   Total Items: {results_summary.get('total_items', 0)}")
        print(f"   News Items: {results_summary.get('news_items', 0)}")
        print(f"   Ad Items: {results_summary.get('ad_items', 0)}")
        print(f"   Ad Ratio: {results_summary.get('ad_ratio', 0)}%")
        
        # Placement positions
        positions = results.get("placement_positions", [])
        if positions:
            print(f"\n📍 Ad Placement Positions:")
            for pos in positions:
                print(f"   Position {pos.get('position')}: {pos.get('type').upper()} - {pos.get('title')}")
        
        # Feed preview
        feed_preview = results.get("feed_preview", [])
        if feed_preview:
            print(f"\n📰 Feed Preview (First 10 items):")
            for i, item in enumerate(feed_preview, 1):
                item_type = item.get("type", "unknown").upper()
                title = item.get("title", "No title")[:40] + "..." if len(item.get("title", "")) > 40 else item.get("title", "No title")
                
                if item_type == "ADVERTISEMENT":
                    print(f"   {i}. 📢 {item_type}: {title}")
                    print(f"      🎯 Relevance: {item.get('relevance_score', 0):.2f}")
                    print(f"      ⭐ Priority: {item.get('priority', 0)}")
                else:
                    print(f"   {i}. 📰 {item_type}: {title}")
    
    def display_targeted_ads(self, ads_data: Dict[str, Any]):
        """Display targeted ads for user"""
        print("\n🎯 **Targeted Ads for User**")
        print("=" * 50)
        
        if not ads_data:
            print("❌ No ads available")
            return
        
        ads = ads_data.get("ads", [])
        print(f"📊 Total Targeted Ads: {len(ads)}")
        
        for i, ad in enumerate(ads, 1):
            print(f"\n{i}. 📢 {ad.get('title', 'No Title')}")
            print(f"   🎯 Relevance Score: {ad.get('relevance_score', 0):.2f}")
            print(f"   ⭐ Priority: {ad.get('priority', 0)}")
            
            # Targeting info
            targeting = ad.get("targeting", {})
            location = targeting.get("location", {})
            demographics = targeting.get("demographics", {})
            
            print(f"   📍 Target Location: State={location.get('state_id')}, District={location.get('district_id')}, City={location.get('city_id')}")
            print(f"   👥 Target Demographics: {demographics.get('target_gender')}, Age {demographics.get('target_age_range')}")
            
            # Schedule info
            schedule = ad.get("schedule", {})
            print(f"   📅 Schedule: {schedule.get('start_date')} to {schedule.get('end_date')}")
            print(f"   ✅ Active: {schedule.get('is_active', False)}")
    
    def interactive_menu(self):
        """Interactive testing menu"""
        print("\n🎯 **Ad Placement Testing Menu**")
        print("=" * 50)
        print("1. 📋 View Ad Placement Configuration")
        print("2. 🧪 Test Ad Placement (by user UID)")
        print("3. 🎯 Get Targeted Ads (requires auth)")
        print("4. 📊 View Ad Performance (requires auth)")
        print("5. 🔄 Test Multiple Users")
        print("6. ❌ Exit")
        
        while True:
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == "1":
                config = self.get_ad_config()
                self.display_config(config)
            
            elif choice == "2":
                user_uid = input("Enter user UID: ").strip()
                if user_uid:
                    news_count = input("Enter news count (default 20): ").strip()
                    news_count = int(news_count) if news_count.isdigit() else 20
                    
                    results = self.test_ad_placement(user_uid, news_count)
                    self.display_placement_results(results)
                else:
                    print("❌ Please enter a valid user UID")
            
            elif choice == "3":
                token = input("Enter auth token (or press Enter to skip): ").strip()
                if token:
                    ads_data = self.get_targeted_ads(token)
                    self.display_targeted_ads(ads_data)
                else:
                    print("❌ Authentication required for targeted ads")
            
            elif choice == "4":
                token = input("Enter auth token: ").strip()
                ad_id = input("Enter ad ID: ").strip()
                if token and ad_id.isdigit():
                    analytics = self.get_ad_analytics(int(ad_id), token)
                    print(f"\n📊 Ad Analytics:")
                    print(json.dumps(analytics, indent=2, default=str))
                else:
                    print("❌ Valid token and ad ID required")
            
            elif choice == "5":
                print("\n🔄 Testing multiple users...")
                test_users = ["test_user_1", "test_user_2", "test_user_3"]
                
                for user_uid in test_users:
                    print(f"\n🧪 Testing user: {user_uid}")
                    results = self.test_ad_placement(user_uid, 15)
                    
                    if results:
                        summary = results.get("results", {})
                        print(f"   ✅ Total Items: {summary.get('total_items', 0)}")
                        print(f"   📢 Ads Placed: {summary.get('ad_items', 0)}")
                        print(f"   📊 Ad Ratio: {summary.get('ad_ratio', 0)}%")
                    else:
                        print(f"   ❌ Test failed for {user_uid}")
            
            elif choice == "6":
                print("👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid choice. Please try again.")
    
    def run(self):
        """Run the interactive tester"""
        print("🎯 **Ad Placement Testing Client**")
        print("=" * 50)
        
        # Test connection
        if not self.test_connection():
            print("❌ Cannot connect to server. Make sure it's running on http://localhost:8001")
            return
        
        print("✅ Connected to server successfully!")
        
        # Show initial config
        config = self.get_ad_config()
        self.display_config(config)
        
        # Start interactive menu
        self.interactive_menu()

if __name__ == "__main__":
    tester = AdPlacementTester()
    tester.run()
