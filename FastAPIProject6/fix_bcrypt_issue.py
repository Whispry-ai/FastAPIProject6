#!/usr/bin/env python3
"""
Fix bcrypt version compatibility issue
"""

import subprocess
import sys

def fix_bcrypt_issue():
    """Fix bcrypt version compatibility"""
    print("🔧 Fixing bcrypt version compatibility...")
    
    try:
        # Upgrade bcrypt to latest version
        print("📦 Upgrading bcrypt...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "bcrypt"], 
                          capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ bcrypt upgraded successfully")
        else:
            print(f"❌ bcrypt upgrade failed: {result.stderr}")
        
        # Upgrade passlib to latest version
        print("📦 Upgrading passlib...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "passlib"], 
                          capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ passlib upgraded successfully")
        else:
            print(f"❌ passlib upgrade failed: {result.stderr}")
        
        # Install specific compatible versions if needed
        print("📦 Installing compatible versions...")
        commands = [
            [sys.executable, "-m", "pip", "install", "bcrypt==4.1.2"],
            [sys.executable, "-m", "pip", "install", "passlib[bcrypt]"]
        ]
        
        for cmd in commands:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Command executed: {' '.join(cmd[4:])}")
            else:
                print(f"❌ Command failed: {result.stderr}")
        
        print("\n🔄 Please restart your server after fixing dependencies")
        
    except Exception as e:
        print(f"❌ Error fixing bcrypt: {str(e)}")

def main():
    print("🚀 Fix bcrypt Compatibility Issue")
    print("=" * 50)
    
    fix_bcrypt_issue()
    
    print("\n" + "=" * 50)
    print("💡 After fixing:")
    print("   1. Restart your server")
    print("   2. Try the user creation again")
    print("   3. Test login with kamineniaswini@gmail.com")

if __name__ == "__main__":
    main()
