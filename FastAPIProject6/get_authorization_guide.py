#!/usr/bin/env python3
"""
Complete Authorization Guide for Enhanced News Application
Shows how to get authentication tokens for locked endpoints
"""

import requests
import json
import webbrowser

BASE_URL = "http://localhost:8001"

def show_authorization_methods():
    """Show all available authorization methods"""
    print("🔐 **How to Get Authorization for Locked Endpoints**")
    print("=" * 70)
    
    print("\n📋 **Available Authorization Methods:**")
    print("-" * 50)
    
    methods = [
        {
            "method": "Google OAuth Login",
            "description": "Login with Google account",
            "steps": [
                "Go to http://localhost:8001/docs",
                "Click 'Authorize' button",
                "Select 'Google OAuth' or 'oauth2'",
                "Click 'Authorize' with Google",
                "Complete Google login flow",
                "Copy the access token"
            ],
            "best_for": "New users, Google account holders"
        },
        {
            "method": "Guest Access",
            "description": "Limited access without full registration",
            "steps": [
                "Use guest endpoints directly",
                "Limited to public features only",
                "Cannot access AI features or user data"
            ],
            "best_for": "Testing public endpoints only"
        },
        {
            "method": "Direct Token Request",
            "description": "Get token via API call",
            "steps": [
                "POST to /auth/login with credentials",
                "OR POST to /auth/google for OAuth",
                "Extract token from response",
                "Use token in Authorization header"
            ],
            "best_for": "Programmatic access, testing"
        }
    ]
    
    for i, method in enumerate(methods, 1):
        print(f"\n{i}. **{method['method']}**")
        print(f"   📝 {method['description']}")
        print(f"   ✨ Best for: {method['best_for']}")
        print(f"   📋 Steps:")
        for step in method['steps']:
            print(f"      • {step}")

def show_google_oauth_process():
    """Show detailed Google OAuth process"""
    print("\n🔍 **Google OAuth Authorization Process**")
    print("=" * 50)
    
    print("\n**Step 1: Open Swagger UI**")
    print("   🌐 Go to: http://localhost:8001/docs")
    
    print("\n**Step 2: Find Authorize Button**")
    print("   🔍 Look for green 'Authorize' button at top right")
    print("   📱 Click the button to open authorization dialog")
    
    print("\n**Step 3: Select OAuth Scope**")
    print("   📋 Check the box for available OAuth scopes")
    print("   ✅ Usually shows: 'oauth2' or 'Google OAuth'")
    
    print("\n**Step 4: Authorize**")
    print("   🔐 Click 'Authorize' button in dialog")
    print("   🌐 This will redirect to Google login page")
    
    print("\n**Step 5: Google Login**")
    print("   👤 Enter your Google credentials")
    print("   🔓 Allow the application permissions")
    print("   🔄 Redirect back to Swagger UI")
    
    print("\n**Step 6: Token Received**")
    print("   ✅ You'll see 'Authorized' in green")
    print("   🔑 Token is automatically stored in browser")
    print("   🧪 Now you can test locked endpoints")

def show_programmatic_auth():
    """Show programmatic authentication methods"""
    print("\n💻 **Programmatic Authentication**")
    print("=" * 50)
    
    print("\n**Method 1: Direct API Call**")
    print("```python")
    print("import requests")
    print()
    print("# Try Google OAuth endpoint")
    print("response = requests.post('http://localhost:8001/auth/google')")
    print("if response.status_code == 200:")
    print("    data = response.json()")
    print("    token = data.get('access_token')")
    print("    print('Token:', token)")
    print("else:")
    print("    print('Error:', response.text)")
    print("```")
    
    print("\n**Method 2: Using Token in Requests**")
    print("```python")
    print("# Once you have the token")
    print("headers = {'Authorization': f'Bearer {token}'}")
    print()
    print("# Test AI endpoint")
    print("response = requests.post(")
    print("    'http://localhost:8001/ai/sentiment-analysis',")
    print("    headers=headers,")
    print("    json={'text': 'This is great news!', 'language': 'en'}")
    print(")")
    print()
    print("print(response.json())")
    print("```")
    
    print("\n**Method 3: Using curl**")
    print("```bash")
    print("# First get token")
    print("curl -X POST http://localhost:8001/auth/google")
    print()
    print("# Then use token")
    print("curl -H 'Authorization: Bearer YOUR_TOKEN' \\")
    print("     -X POST http://localhost:8001/ai/sentiment-analysis \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{\"text\": \"Great news!\", \"language\": \"en\"}'")
    print("```")

def show_troubleshooting():
    """Show troubleshooting tips"""
    print("\n🔧 **Troubleshooting Authorization Issues**")
    print("=" * 50)
    
    issues = [
        {
            "problem": "Authorize button not working",
            "solution": [
                "Refresh the Swagger UI page",
                "Check server is running on port 8001",
                "Verify no browser pop-up blockers",
                "Try different browser (Chrome, Firefox)"
            ]
        },
        {
            "problem": "Google OAuth redirect error",
            "solution": [
                "Check redirect URI in Google Console",
                "Ensure http://localhost:8001 is registered",
                "Verify OAuth client ID is correct",
                "Check Google API is enabled"
            ]
        },
        {
            "problem": "Token expired or invalid",
            "solution": [
                "Get fresh token from authorize button",
                "Check token format: 'Bearer TOKEN'",
                "Verify token not expired",
                "Clear browser cache and retry"
            ]
        },
        {
            "problem": "401 Unauthorized error",
            "solution": [
                "Ensure token is included in Authorization header",
                "Check token spelling and format",
                "Verify token hasn't expired",
                "Re-authorize with fresh token"
            ]
        }
    ]
    
    for issue in issues:
        print(f"\n❌ **{issue['problem']}**")
        print("   💡 Solutions:")
        for solution in issue['solution']:
            print(f"      • {solution}")

def show_test_examples():
    """Show practical test examples"""
    print("\n🧪 **Test Authorization with Examples**")
    print("=" * 50)
    
    print("\n**Example 1: Test Public Endpoint (No Auth Needed)**")
    print("```python")
    print("import requests")
    print()
    print("# Public endpoint - no token required")
    print("response = requests.get('http://localhost:8001/health')")
    print("print('Health Check:', response.json())")
    print()
    print("response = requests.get('http://localhost:8001/ai/supported-languages')")
    print("print('Supported Languages:', response.json())")
    print("```")
    
    print("\n**Example 2: Test AI Endpoint (Auth Required)**")
    print("```python")
    print("import requests")
    print()
    print("# Get token first (you'll get this from Swagger UI)")
    print("token = 'YOUR_TOKEN_HERE'  # Replace with actual token")
    print("headers = {'Authorization': f'Bearer {token}'}")
    print()
    print("# Test sentiment analysis")
    print("response = requests.post(")
    print("    'http://localhost:8001/ai/sentiment-analysis',")
    print("    headers=headers,")
    print("    json={'text': 'This is amazing news!', 'language': 'en'}")
    print(")")
    print()
    print("if response.status_code == 200:")
    print("    print('AI Analysis Result:', response.json())")
    print("else:")
    print("    print('Error:', response.status_code, response.text)")
    print("```")

def show_current_auth_config():
    """Show current authentication configuration"""
    print("\n⚙️ **Current Authentication Configuration**")
    print("=" * 50)
    
    print("\n🔑 **OAuth Configuration:**")
    print("   • Client ID: 775805061826-jdbjbqa9is88m5qt5tbt60aouk9i7vdo.apps.googleusercontent.com")
    print("   • Provider: Google OAuth 2.0")
    print("   • Scopes: Basic profile and email")
    
    print("\n🏛️ **User Roles:**")
    print("   • GUEST (1): Read public content")
    print("   • USER (2): Bookmark, vote, AI features")
    print("   • PUBLISHER (3): Publish content")
    print("   • EMPLOYEE (4): Moderate, analytics")
    print("   • ADMIN (5): Full access")
    
    print("\n🔐 **Token Format:**")
    print("   • Type: JWT Bearer Token")
    print("   • Header: Authorization: Bearer <token>")
    print("   • Expiry: Usually 24 hours")

def main():
    """Main function"""
    print("🔐 **Complete Authorization Guide**")
    print("=" * 70)
    print("This guide shows you how to get authorization for locked endpoints.")
    print()
    
    show_authorization_methods()
    show_google_oauth_process()
    show_programmatic_auth()
    show_troubleshooting()
    show_test_examples()
    show_current_auth_config()
    
    print(f"\n🎯 **Quick Start Guide:**")
    print("=" * 40)
    print("1. 🌐 Open: http://localhost:8001/docs")
    print("2. 🔐 Click 'Authorize' button (top right)")
    print("3. 📋 Check OAuth scope box")
    print("4. 🔓 Click 'Authorize' and complete Google login")
    print("5. ✅ You'll see 'Authorized' in green")
    print("6. 🧪 Test any locked endpoint (like AI features)")
    
    print(f"\n💡 **Pro Tips:**")
    print("=" * 30)
    print("• Token is stored in browser session")
    print("• Refresh page if authorization issues")
    print("• Use 'Try it out' to test endpoints easily")
    print("• Check console for OAuth errors")
    
    print(f"\n📊 **What You Can Access With Authorization:**")
    print("=" * 50)
    print("🤖 AI Features: Sentiment analysis, fake news detection, categories")
    print("📚 User Features: Profile, bookmarks, notifications")
    print("📢 Ads: Targeted advertisements, performance analytics")
    print("📈 Analytics: Dashboard, content performance, user analytics")
    print("📁 Files: Upload images and videos")

if __name__ == "__main__":
    main()
