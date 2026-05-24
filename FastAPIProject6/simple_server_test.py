#!/usr/bin/env python3
"""
Simple server start and test
"""

import subprocess
import time
import requests
import signal
import sys

BASE_URL = "http://127.0.0.1:8000"

def main():
    print("🚀 Simple Server Start & Test")
    print("=" * 40)
    
    print("📋 Instructions:")
    print("1. This will start the server")
    print("2. Then test rewards system")
    print("3. Press Ctrl+C to stop")
    print()
    
    # Start server
    print("🚀 Starting server...")
    try:
        # Start server process
        process = subprocess.Popen([
            "python", "-m", "uvicorn", "main:app", "--port", "8000"
        ], 
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
        )
        
        print("✅ Server starting...")
        print("📡 Waiting 5 seconds for startup...")
        
        # Wait for startup
        time.sleep(5)
        
        # Test server
        print("🌐 Testing server connection...")
        try:
            response = requests.get(f"{BASE_URL}/", timeout=3)
            print(f"✅ Server responding! Status: {response.status_code}")
        except:
            print("❌ Server not responding yet, waiting more...")
            time.sleep(3)
        
        print()
        print("🎁 Now you can test rewards system:")
        print("📖 API Docs: http://127.0.0.1:8000/docs")
        print("🎁 Test with: python rewards_test_quick.py")
        print()
        print("🛑 Press Ctrl+C to stop server")
        
        # Keep running
        process.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping server...")
        if 'process' in locals():
            process.terminate()
        print("✅ Server stopped")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("💡 Try manual start: python -m uvicorn main:app --port 8000")

if __name__ == "__main__":
    main()
