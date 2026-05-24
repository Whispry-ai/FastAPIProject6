#!/usr/bin/env python3
"""
🎯 QUICK FIX FOR REWARDS IMPORT ERROR
Fix the specific InsightStoryCreate import issue
"""

import os

def main():
    print("🔧 QUICK FIX FOR REWARDS IMPORT ERROR")
    print("=" * 50)
    
    # Check what's in schemas folder
    schemas_dir = os.path.join(os.path.dirname(__file__), 'schemas')
    if os.path.exists(schemas_dir):
        print(f"📁 Schemas directory: {schemas_dir}")
        files = os.listdir(schemas_dir)
        print(f"📄 Files in schemas: {files}")
        
        # Check if insights.py exists
        insights_path = os.path.join(schemas_dir, 'insights.py')
        if os.path.exists(insights_path):
            print(f"✅ insights.py exists")
            with open(insights_path, 'r') as f:
                content = f.read()
                if 'InsightStoryCreate' in content:
                    print("✅ InsightStoryCreate found in insights.py")
                else:
                    print("❌ InsightStoryCreate NOT found in insights.py")
        else:
            print("❌ insights.py does not exist")
    
    # Check what's in __init__.py
    init_path = os.path.join(schemas_dir, '__init__.py')
    if os.path.exists(init_path):
        print(f"📄 Current __init__.py content:")
        with open(init_path, 'r') as f:
            content = f.read()
            print(content)
    
    print("\n🔧 **QUICK FIX OPTIONS:**")
    print("\n📋 Option 1: Add to __init__.py")
    print("   Add this line to schemas/__init__.py:")
    print("   from .insights import InsightStoryCreate")
    
    print("\n📋 Option 2: Change import in insights_router.py")
    print("   Change line 15 in routes/insights_router.py from:")
    print("   from schemas import (")
    print("   To:")
    print("   from schemas.insights import InsightStoryCreate")
    
    print("\n📋 Option 3: Check file names")
    print("   Make sure class is named exactly 'InsightStoryCreate'")
    print("   Check for typos: 'InsightStoryCreate' vs 'InsightStorycreate'")
    
    print("\n🎯 **TEST THE FIX:**")
    print("   1. Apply Option 1 or 2")
    print("   2. Restart main server: python -m uvicorn main:app --port 8001")
    print("   3. Test rewards: http://localhost:8001/docs")

if __name__ == "__main__":
    main()
