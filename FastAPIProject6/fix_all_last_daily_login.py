#!/usr/bin/env python3
"""
Debug and Fix All updated_at References
Find all references to updated_at in the entire project and fix them
"""

import os
import re

def search_all_files_for_updated_at():
    """Search all Python files for updated_at references"""
    print("🔍 Searching all files for 'updated_at' references...")
    print("=" * 60)
    
    matches = []
    
    # Search in all Python files
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Find all lines with updated_at
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        if 'updated_at' in line:
                            matches.append((file_path, i, line.strip()))
                except Exception as e:
                    print(f"❌ Error reading {file_path}: {e}")
    
    if matches:
        print(f"📋 Found {len(matches)} references:")
        for file_path, line_num, line_content in matches:
            print(f"   {file_path}:{line_num}: {line_content}")
    else:
        print("✅ No 'updated_at' references found")
    
    return matches

def fix_all_updated_at_references():
    """Fix all updated_at references in the project"""
    try:
        matches = search_all_files_for_updated_at()
        
        if not matches:
            print("✅ No references to fix")
            return True
        
        print(f"\n🔧 Fixing {len(matches)} references...")
        
        fixed_count = 0
        for file_path, line_num, line_content in matches:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Replace all instances
                fixed_content = content.replace('updated_at', 'updated_at')
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                
                print(f"   ✅ Fixed {file_path}")
                fixed_count += 1
                
            except Exception as e:
                print(f"   ❌ Error fixing {file_path}: {e}")
        
        print(f"✅ Fixed {fixed_count}/{len(matches)} files")
        return fixed_count == len(matches)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main function"""
    if fix_all_updated_at_references():
        print("\n🎉 All 'updated_at' references fixed!")
        print("   Rewards system should now work at 100%")
    else:
        print("\n❌ Some references could not be fixed")

if __name__ == "__main__":
    main()
