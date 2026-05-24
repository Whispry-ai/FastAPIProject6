#!/usr/bin/env python3
"""
Test file to verify file opening and basic functionality
"""

def test_file_operations():
    """Test basic file operations"""
    try:
        # Test reading the main application file
        with open('main.py', 'r') as f:
            content = f.read()
            print(f"✅ Successfully read main.py ({len(content)} characters)")
        
        # Test reading database configuration
        with open('database.py', 'r') as f:
            content = f.read()
            print(f"✅ Successfully read database.py ({len(content)} characters)")
        
        # Test database file existence
        import os
        if os.path.exists('news_platform.db'):
            print("✅ Database file exists: news_platform.db")
        else:
            print("⚠️  Database file not found: news_platform.db")
        
        print("🎉 All file operations completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during file operations: {e}")

if __name__ == "__main__":
    test_file_operations()
