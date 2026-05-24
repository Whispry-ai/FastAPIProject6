#!/usr/bin/env python3
"""
Find AI Endpoints in Swagger/OpenAPI Documentation
Locates all AI features in the API documentation
"""

import requests
import json

def find_ai_endpoints():
    """Find all AI endpoints in the OpenAPI documentation"""
    print("🔍 **Finding AI Features in Swagger Documentation**")
    print("=" * 60)
    
    try:
        # Get OpenAPI documentation
        response = requests.get("http://localhost:8001/openapi.json", timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Cannot connect to server: {response.status_code}")
            return
        
        data = response.json()
        paths = data.get("paths", {})
        
        # Find AI endpoints
        ai_endpoints = {}
        
        for path, methods in paths.items():
            if "ai" in path:
                ai_endpoints[path] = methods
        
        print(f"\n🤖 **AI Endpoints Found: {len(ai_endpoints)}**")
        print("-" * 40)
        
        if not ai_endpoints:
            print("❌ No AI endpoints found in documentation")
            print("\n🔧 **Possible Issues:**")
            print("   • Server not running")
            print("   • AI routes not properly registered")
            print("   • Import errors in ai_routes.py")
            
            print("\n🚀 **Solutions:**")
            print("   1. Start server: python -m uvicorn main:app --port 8001")
            print("   2. Check imports in routes/ai_routes.py")
            print("   3. Verify router inclusion in main.py")
            return
        
        # Display AI endpoints
        for path, methods in ai_endpoints.items():
            print(f"\n📍 **{path}**")
            for method, details in methods.items():
                method_upper = method.upper()
                summary = details.get("summary", "No summary")
                description = details.get("description", "No description")
                
                print(f"   {method_upper}: {summary}")
                if description != "No description":
                    print(f"   📝 {description[:100]}...")
                
                # Check if authentication is required
                security = details.get("security", [])
                if security:
                    print(f"   🔒 Authentication Required")
                else:
                    print(f"   🌐 Public Access")
        
        print(f"\n📋 **AI Endpoints Summary:**")
        print("-" * 40)
        for path in ai_endpoints.keys():
            print(f"   🤖 {path}")
        
        print(f"\n🌐 **Access in Swagger UI:**")
        print("-" * 40)
        print("   1. Open: http://localhost:8001/docs")
        print("   2. Look for 'AI' section in the sidebar")
        print("   3. Click on any AI endpoint to expand")
        print("   4. Click 'Try it out' to test")
        
        return ai_endpoints
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection Error: {str(e)}")
        print("\n🔧 **Make sure server is running:**")
        print("   python -m uvicorn main:app --port 8001 --host 0.0.0.0")
    except json.JSONDecodeError as e:
        print(f"❌ JSON Error: {str(e)}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def check_swagger_ui():
    """Check if Swagger UI is accessible"""
    print("\n🌐 **Checking Swagger UI Access**")
    print("=" * 40)
    
    try:
        response = requests.get("http://localhost:8001/docs", timeout=5)
        
        if response.status_code == 200:
            print("✅ Swagger UI is accessible")
            print("🌐 URL: http://localhost:8001/docs")
            
            print("\n📋 **How to Find AI Features in Swagger:**")
            print("-" * 40)
            print("   1. Open http://localhost:8001/docs in browser")
            print("   2. Look for 'AI' tag/section in the sidebar")
            print("   3. Expand AI endpoints (click the arrow)")
            print("   4. Click on any endpoint to see details")
            print("   5. Click 'Try it out' button")
            print("   6. Fill in required fields")
            print("   7. Click 'Execute' to test")
            
            print("\n🔍 **AI Endpoints to Look For:**")
            print("-" * 40)
            ai_endpoints_list = [
                "POST /ai/sentiment-analysis",
                "POST /ai/fake-news-detection", 
                "POST /ai/category-suggestion",
                "POST /ai/content-analysis",
                "POST /ai/csv-analysis",
                "GET /ai/csv-template",
                "GET /ai/supported-languages"
            ]
            
            for endpoint in ai_endpoints_list:
                print(f"   🤖 {endpoint}")
                
        else:
            print(f"❌ Swagger UI not accessible: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot access Swagger UI: {str(e)}")
        print("\n🔧 **Start the server first:**")
        print("   python -m uvicorn main:app --port 8001 --host 0.0.0.0")

def show_ai_endpoint_details():
    """Show detailed information about AI endpoints"""
    print("\n📖 **AI Endpoint Details**")
    print("=" * 40)
    
    ai_details = [
        {
            "endpoint": "POST /ai/sentiment-analysis",
            "description": "Analyze text sentiment with emotion detection",
            "input": {"text": "string", "language": "en|te|hi"},
            "auth": "Required",
            "section": "AI"
        },
        {
            "endpoint": "POST /ai/fake-news-detection",
            "description": "Detect fake news with credibility scoring",
            "input": {"title": "string", "content": "string"},
            "auth": "Required", 
            "section": "AI"
        },
        {
            "endpoint": "POST /ai/category-suggestion",
            "description": "Suggest categories for news content",
            "input": {"text": "string"},
            "auth": "Required",
            "section": "AI"
        },
        {
            "endpoint": "POST /ai/content-analysis",
            "description": "Complete AI analysis of content",
            "input": {"text": "string", "analysis_type": "comprehensive"},
            "auth": "Required",
            "section": "AI"
        },
        {
            "endpoint": "POST /ai/csv-analysis",
            "description": "Batch process CSV files with AI analysis",
            "input": {"file": "CSV file"},
            "auth": "Required",
            "section": "AI"
        },
        {
            "endpoint": "GET /ai/csv-template",
            "description": "Download CSV template for batch analysis",
            "input": "None",
            "auth": "None",
            "section": "AI"
        },
        {
            "endpoint": "GET /ai/supported-languages",
            "description": "Get list of supported AI languages",
            "input": "None",
            "auth": "None",
            "section": "AI"
        }
    ]
    
    for ai in ai_details:
        print(f"\n🤖 {ai['endpoint']}")
        print(f"   📝 {ai['description']}")
        print(f"   📥 Input: {ai['input']}")
        print(f"   🔐 Auth: {ai['auth']}")
        print(f"   📂 Section: {ai['section']}")

def main():
    """Main function"""
    print("🔍 **AI Features in Swagger Documentation Finder**")
    print("=" * 60)
    print("This script helps you locate AI features in the Swagger UI.")
    print()
    
    # Find AI endpoints
    ai_endpoints = find_ai_endpoints()
    
    # Check Swagger UI
    check_swagger_ui()
    
    # Show details
    show_ai_endpoint_details()
    
    print(f"\n🎯 **Quick Guide to Find AI Features in Swagger:**")
    print("=" * 50)
    print("1. 🌐 Open: http://localhost:8001/docs")
    print("2. 🔍 Look for 'AI' section in sidebar")
    print("3. 📋 Expand AI endpoints (click ▼)")
    print("4. 🧪 Click 'Try it out' button")
    print("5. 🔐 Login if required (Authorize button)")
    print("6. 📝 Fill in required parameters")
    print("7. ⚡ Click 'Execute' to test")
    
    print(f"\n💡 **If AI Features Not Visible:**")
    print("=" * 30)
    print("• Check server is running on port 8001")
    print("• Verify ai_routes.py has no import errors")
    print("• Ensure router is included in main.py")
    print("• Look for any console error messages")

if __name__ == "__main__":
    main()
