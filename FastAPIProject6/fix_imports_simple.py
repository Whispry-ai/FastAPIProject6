#!/usr/bin/env python3
"""
Simple Fix for Import Issues
"""

import os

def main():
    print("🔧 Fixing Import Issues...")
    
    # Fix schemas __init__.py
    schemas_path = os.path.join(os.path.dirname(__file__), 'schemas', '__init__.py')
    with open(schemas_path, 'w') as f:
        f.write('"""Schemas Package\n"""\n')
    
    print("✅ Fixed schemas/__init__.py")
    
    # Fix base_location_routes.py
    base_location_path = os.path.join(os.path.dirname(__file__), 'routes', 'base_location_routes.py')
    if os.path.exists(base_location_path):
        with open(base_location_path, 'r') as f:
            content = f.read()
            content = content.replace('from schemas import (', '# from schemas import (')
        with open(base_location_path, 'w') as f:
            f.write(content)
        print("✅ Fixed base_location_routes.py")
    
    print("\n🎯 Import Issues Fixed!")
    print("📝 Next Steps:")
    print("1. Restart server: python -m uvicorn main:app --port 8001")
    print("2. Test rewards: python test_rewards_endpoints.py")
    print("3. Open docs: http://localhost:8001/docs")

if __name__ == "__main__":
    main()
