#!/usr/bin/env python3
"""
Find and Remove All updated_at References
Find all references to updated_at and remove them
"""

import re

def find_all_updated_at_refs():
    """Find all references to updated_at in rewards service"""
    try:
        with open('services/rewards_service.py', 'r') as f:
            content = f.read()
        
        print("🔍 Searching for all 'updated_at' references...")
        
        # Find all lines with updated_at
        lines = content.split('\n')
        matches = []
        
        for i, line in enumerate(lines, 1):
            if 'updated_at' in line:
                matches.append((i, line.strip()))
        
        if matches:
            print(f"📋 Found {len(matches)} references:")
            for line_num, line_content in matches:
                print(f"   Line {line_num}: {line_content}")
        else:
            print("✅ No 'updated_at' references found")
        
        return matches
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def remove_updated_at_refs():
    """Remove all updated_at references from rewards service"""
    try:
        with open('services/rewards_service.py', 'r') as f:
            content = f.read()
        
        print("\n🧹 Removing all 'updated_at' references...")
        
        # Replace all instances
        fixed_content = content.replace('updated_at', 'updated_at')
        
        with open('services/rewards_service.py', 'w') as f:
            f.write(fixed_content)
        
        print("✅ All 'updated_at' references removed")
        
        # Verify removal
        if 'updated_at' not in fixed_content:
            print("✅ Verification successful - no references remain")
        else:
            print("❌ Some references still remain")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main function"""
    matches = find_all_updated_at_refs()
    
    if matches:
        print(f"\n⚠️  Found {len(matches)} references that need to be removed")
        remove_updated_at_refs()
    else:
        print("\n✅ No 'updated_at' references found - service is clean")

if __name__ == "__main__":
    main()
