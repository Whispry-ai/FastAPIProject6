#!/usr/bin/env python3
"""
Test AI routes directly
"""

import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_ai_routes_direct():
    """Test AI routes directly"""
    print("🔍 **Testing AI Routes Directly**")
    print("=" * 40)
    
    try:
        # Import AI routes directly
        from routes.ai_routes import router
        print("✅ AI router imported directly")
        
        # Check router routes
        print(f"Router type: {type(router)}")
        
        # Check if routes are registered
        if hasattr(router, 'routes'):
            routes = router.routes
            print(f"Number of routes: {len(routes)}")
            
            # Print all routes
            for i, route in enumerate(routes):
                if hasattr(route, 'path'):
                    print(f"   📍 Route {i+1}: {route.path} ({route.methods if hasattr(route, 'methods') else 'N/A'})")
                elif hasattr(route, 'path'):
                    print(f"   📍 Route {i+1}: {route.path}")
        else:
            print("❌ Router has no routes attribute")
        
        # Try to access a specific route
        try:
            # Check if sentiment analysis route exists
            print("\n🔍 Checking specific routes...")
            
            # Look for sentiment analysis route
            found_sentiment = False
            for route in router.routes:
                if hasattr(route, 'path') and 'sentiment-analysis' in str(route.path):
                    found_sentiment = True
                    print(f"✅ Found sentiment analysis route: {route.path}")
                    break
            
            if not found_sentiment:
                print("❌ Sentiment analysis route not found")
                
        except Exception as e:
            print(f"❌ Error checking routes: {e}")
            
    except Exception as e:
        print(f"❌ Error importing AI routes: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ai_routes_direct()
