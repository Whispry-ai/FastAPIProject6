#!/usr/bin/env python3
"""
How to Use Your Authorization Token
Shows exactly how to use your token to access locked endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def show_how_to_use_token():
    """Show how to use the authorization token"""
    print("🎯 **How to Use Your Authorization Token**")
    print("=" * 60)
    
    print("\n✅ **Great! You have the token. Now use it:**")
    print("-" * 50)
    
    print("\n**Method 1: In Swagger UI (Easiest)**")
    print("-" * 40)
    print("1. 🌐 Go to: http://localhost:8001/docs")
    print("2. 🔐 Click 'Authorize' button (top right)")
    print("3. 📝 Paste your token in the format: Bearer YOUR_TOKEN")
    print("4. ✅ Click 'Authorize'")
    print("5. 🧪 Test any locked endpoint (AI, bookmarks, etc.)")
    
    print("\n**Method 2: In Python Code**")
    print("-" * 40)
    print("```python")
    print("import requests")
    print()
    print("# Your token")
    print("token = 'YOUR_TOKEN_HERE'  # Replace with your actual token")
    print("headers = {'Authorization': f'Bearer {token}'}")
    print()
    print("# Test AI sentiment analysis")
    print("response = requests.post(")
    print("    'http://localhost:8001/ai/sentiment-analysis',")
    print("    headers=headers,")
    print("    json={'text': 'This is amazing news!', 'language': 'en'}")
    print(")")
    print("print(response.json())")
    print("```")
    
    print("\n**Method 3: With curl**")
    print("-" * 40)
    print("```bash")
    print("# Replace YOUR_TOKEN with your actual token")
    print("curl -H 'Authorization: Bearer YOUR_TOKEN' \\")
    print("     -X POST http://localhost:8001/ai/sentiment-analysis \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{\"text\": \"Great news!\", \"language\": \"en\"}'")
    print("```")

def test_with_token_examples():
    """Show practical examples with token"""
    print("\n🧪 **Test Examples With Your Token**")
    print("=" * 50)
    
    examples = [
        {
            "endpoint": "AI Sentiment Analysis",
            "method": "POST",
            "url": "/ai/sentiment-analysis",
            "data": {"text": "This is wonderful news about technology!", "language": "en"},
            "description": "Analyze text sentiment with AI"
        },
        {
            "endpoint": "AI Fake News Detection",
            "method": "POST", 
            "url": "/ai/fake-news-detection",
            "data": {"title": "Scientists Discover Cure", "content": "Revolutionary breakthrough..."},
            "description": "Detect fake news with AI"
        },
        {
            "endpoint": "AI Category Suggestion",
            "method": "POST",
            "url": "/ai/category-suggestion", 
            "data": {"text": "Tech startup raises funding for AI development"},
            "description": "Get AI suggested categories"
        },
        {
            "endpoint": "User Profile",
            "method": "GET",
            "url": "/user/profile",
            "data": None,
            "description": "Get your user profile"
        },
        {
            "endpoint": "User Bookmarks",
            "method": "GET",
            "url": "/user/bookmarks",
            "data": None,
            "description": "Get your bookmarked news"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. **{example['endpoint']}**")
        print(f"   📝 {example['description']}")
        print(f"   🔗 {example['method']} {example['url']}")
        
        if example['data']:
            print(f"   📥 Data: {example['data']}")
        
        print(f"   🧪 Test Code:")
        if example['data']:
            print(f"   ```python")
            print(f"   response = requests.{example['method'].lower()}(")
            print(f"       'http://localhost:8001{example['url']}',")
            print(f"       headers=headers,")
            print(f"       json={example['data']}")
            print(f"   )")
            print(f"   ```")
        else:
            print(f"   ```python")
            print(f"   response = requests.{example['method'].lower()}(")
            print(f"       'http://localhost:8001{example['url']}',")
            print(f"       headers=headers")
            print(f"   )")
            print(f"   ```")

def show_token_format():
    """Show correct token format"""
    print("\n📝 **Correct Token Format**")
    print("=" * 40)
    
    print("\n✅ **Correct Format:**")
    print("   Authorization: Bearer your_token_here")
    print("   Example: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    
    print("\n❌ **Incorrect Formats:**")
    print("   ❌ your_token_here (missing 'Bearer ')")
    print("   ❌ Token: Bearer your_token_here (wrong header)")
    print("   ❌ bearer your_token_here (lowercase 'bearer')")
    
    print("\n🔧 **In Different Languages:**")
    print("   Python: {'Authorization': f'Bearer {token}'}")
    print("   curl: -H 'Authorization: Bearer TOKEN'")
    print("   JavaScript: headers: {'Authorization': `Bearer ${token}`}")

def show_what_you_can_access():
    """Show what you can access with the token"""
    print("\n🎉 **What You Can Access With Your Token**")
    print("=" * 50)
    
    categories = {
        "🤖 AI Features": [
            "Sentiment analysis with emotion detection",
            "Fake news detection with credibility scoring", 
            "Category suggestions for content",
            "Comprehensive content analysis",
            "CSV batch processing",
            "Multi-language support (English, Telugu, Hindi)"
        ],
        "📚 User Features": [
            "Personal profile management",
            "Bookmarked news articles",
            "Reading history and preferences",
            "Personalized recommendations",
            "User statistics and analytics"
        ],
        "📢 Advertisement System": [
            "Targeted advertisements",
            "Ad performance analytics",
            "Placement strategy optimization",
            "Revenue tracking",
            "Campaign management"
        ],
        "📈 Analytics Dashboard": [
            "Content performance metrics",
            "User engagement analytics", 
            "Location-based statistics",
            "Trending topics analysis",
            "Real-time dashboard data"
        ],
        "📁 File Management": [
            "Upload images and videos",
            "File processing and optimization",
            "Thumbnail generation",
            "Media organization"
        ],
        "📰 Enhanced News": [
            "Personalized news feed",
            "Trending topics",
            "Recommended articles",
            "Bookmark and report functionality"
        ]
    }
    
    for category, features in categories.items():
        print(f"\n{category}:")
        for feature in features:
            print(f"   ✅ {feature}")

def create_quick_test_script():
    """Create a quick test script"""
    print("\n🚀 **Quick Test Script**")
    print("=" * 40)
    
    script_content = '''
#!/usr/bin/env python3
import requests
import json

# Replace with your actual token
TOKEN = "YOUR_TOKEN_HERE"  # <-- PASTE YOUR TOKEN HERE
BASE_URL = "http://localhost:8001"

def test_ai_features():
    """Test AI features with your token"""
    headers = {'Authorization': f'Bearer {TOKEN}'}
    
    print("🧪 Testing AI Features...")
    
    # Test 1: Sentiment Analysis
    print("\\n1. Testing Sentiment Analysis:")
    response = requests.post(
        f"{BASE_URL}/ai/sentiment-analysis",
        headers=headers,
        json={'text': 'This is amazing news about technology!', 'language': 'en'}
    )
    
    if response.status_code == 200:
        print("✅ Success:", response.json())
    else:
        print("❌ Error:", response.status_code, response.text)
    
    # Test 2: Category Suggestion
    print("\\n2. Testing Category Suggestion:")
    response = requests.post(
        f"{BASE_URL}/ai/category-suggestion",
        headers=headers,
        json={'text': 'Tech company launches new AI product'}
    )
    
    if response.status_code == 200:
        print("✅ Success:", response.json())
    else:
        print("❌ Error:", response.status_code, response.text)
    
    # Test 3: User Profile
    print("\\n3. Testing User Profile:")
    response = requests.get(
        f"{BASE_URL}/user/profile",
        headers=headers
    )
    
    if response.status_code == 200:
        print("✅ Success:", response.json())
    else:
        print("❌ Error:", response.status_code, response.text)

if __name__ == "__main__":
    if TOKEN == "YOUR_TOKEN_HERE":
        print("❌ Please replace YOUR_TOKEN_HERE with your actual token")
        print("🔐 Get your token from: http://localhost:8001/docs")
    else:
        test_ai_features()
'''
    
    print("Create a file called `test_with_token.py` and paste this code:")
    print("```python")
    print(script_content)
    print("```")
    print("\nThen run: python test_with_token.py")

def main():
    """Main function"""
    print("🎯 **Using Your Authorization Token - Complete Guide**")
    print("=" * 70)
    print("You have the token! Here's exactly how to use it.")
    print()
    
    show_how_to_use_token()
    show_token_format()
    test_with_token_examples()
    show_what_you_can_access()
    create_quick_test_script()
    
    print(f"\n🚀 **Quick Start Right Now:**")
    print("=" * 40)
    print("1. 🌐 Open: http://localhost:8001/docs")
    print("2. 🔐 Click 'Authorize' button")
    print("3. 📝 Enter: Bearer YOUR_TOKEN")
    print("4. ✅ Click 'Authorize'")
    print("5. 🧪 Try any AI endpoint!")
    
    print(f"\n💡 **Pro Tip:**")
    print("Once authorized in Swagger UI, the token is stored in your browser")
    print("session. You can test all locked endpoints without re-entering the token!")

if __name__ == "__main__":
    main()
