#!/usr/bin/env python3
"""
Start server on multiple ports
"""

import subprocess
import time
import requests
import signal
import sys

def try_start_server(port):
    """Try to start server on specific port"""
    print(f"🚀 Trying to start server on port {port}...")
    
    try:
        process = subprocess.Popen([
            "python", "-m", "uvicorn", "main:app", "--port", str(port)
        ], 
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
        )
        
        print(f"✅ Server starting on port {port}...")
        
        # Wait for startup
        for i in range(5):
            try:
                response = requests.get(f"http://127.0.0.1:{port}/", timeout=2)
                if response.status_code == 200:
                    print(f"✅ Server is ready on port {port}!")
                    return process
            except:
                pass
            time.sleep(1)
            print(f"⏳ Waiting... {i+1}/5")
        
        print(f"❌ Server failed to start on port {port}")
        process.terminate()
        return None
        
    except Exception as e:
        print(f"❌ Error starting server on port {port}: {str(e)}")
        return None

def main():
    print("🚀 Start Server on Multiple Ports")
    print("=" * 50)
    
    # Try different ports
    ports_to_try = [8000, 8001, 8002, 8003]
    
    for port in ports_to_try:
        process = try_start_server(port)
        if process:
            print(f"\n🎉 Server successfully started on port {port}!")
            print(f"🌐 Server URL: http://127.0.0.1:{port}")
            print(f"📖 API Docs: http://127.0.0.1:{port}/docs")
            print("🛑 Press Ctrl+C to stop server")
            
            try:
                # Keep server running
                process.wait()
            except KeyboardInterrupt:
                print(f"\n🛑 Stopping server on port {port}...")
                process.terminate()
            return
    
    print("\n❌ Failed to start server on any port")
    print("💡 Try manually:")
    print("   python -m uvicorn main:app --port 8001")
    print("   or check what's using port 8000")

if __name__ == "__main__":
    main()
