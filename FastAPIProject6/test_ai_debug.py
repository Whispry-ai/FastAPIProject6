#!/usr/bin/env python3
"""
Debug AI routes registration
"""

import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_ai_routes_import():
    """Test AI routes import and registration"""
    print("🔍 **Testing AI Routes Import**")
    print("=" * 40)
    
    try:
        # Test importing AI routes
        from routes import ai_routes
        print("✅ AI routes imported successfully")
        
        # Check router object
        router = ai_routes.router
        print(f"✅ Router object: {type(router)}")
        
        # Check router routes
        if hasattr(router, 'routes'):
            routes = router.routes
            print(f"✅ Number of routes: {len(routes)}")
            
            # Print route paths
            for route in routes:
                if hasattr(route, 'path'):
                    print(f"   📍 Route: {route.path}")
                elif hasattr(route, 'path'):
                    print(f"   📍 Route: {route.path}")
        
        print("✅ AI routes structure looks correct")
        
    except Exception as e:
        print(f"❌ Error importing AI routes: {e}")

def test_main_app():
    """Test main app import"""
    print("\n🏗️ **Testing Main App Import**")
    print("=" * 40)
    
    try:
        from main import app
        print("✅ Main app imported successfully")
        
        # Check if AI routes are registered
        routes = app.routes
        ai_routes_count = 0
        for route in routes:
            if hasattr(route, 'path') and '/ai' in route.path:
                print(f"   📍 AI Route: {route.path}")
                ai_routes_count += 1
        
        print(f"✅ Found {ai_routes_count} AI routes in app")
        
        if ai_routes_count == 0:
            print("❌ No AI routes found in app - registration issue!")
        else:
            print("✅ AI routes are registered in app")
            
    except Exception as e:
        print(f"❌ Error importing main app: {e}")

if __name__ == "__main__":
    test_ai_routes_import()
    test_main_app()
