#!/usr/bin/env python3
"""
Test News Sharing and View Tracking System
Tests all engagement features with your actual news articles
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8001"

def test_sharing_system():
    """Test the complete sharing and engagement system"""
    print("📱 **Testing News Sharing & Engagement System**")
    print("=" * 60)
    
    # First, get your news articles
    print("\n1. Getting Your News Articles:")
    try:
        response = requests.get(f"{BASE_URL}/news")
        if response.status_code == 200:
            news_data = response.json()
            articles = news_data.get('news', [])
            print(f"✅ Found {len(articles)} news articles")
            
            if not articles:
                print("❌ No news articles found")
                return
            
            # Use the first article for testing
            test_article = articles[0]
            news_uid = test_article.get('news_uid')
            title = test_article.get('title', 'No title')
            
            print(f"📰 Testing with: {title}")
            print(f"🔑 News UID: {news_uid}")
            print(f"👁️ Current views: {test_article.get('views_count', 0)}")
            print(f"❤️ Current likes: {test_article.get('likes_count', 0)}")
            print(f"📤 Current shares: {test_article.get('shares_count', 0)}")
            
        else:
            print("❌ Failed to get news articles")
            return
    except Exception as e:
        print(f"❌ Error getting news: {e}")
        return
    
    # Test 2: Track a view
    print(f"\n2. Tracking a News View:")
    try:
        view_data = {
            "news_uid": news_uid,
            "user_uid": "test123",  # Use our test user
            "viewed_at": datetime.now().isoformat()
        }
        
        response = requests.post(f"{BASE_URL}/news/{news_uid}/view", json=view_data)
        if response.status_code == 200:
            result = response.json()
            print("✅ View tracked successfully")
            print(f"   Message: {result.get('message', 'Success')}")
        else:
            print(f"❌ View tracking failed: {response.text}")
    except Exception as e:
        print(f"❌ Error tracking view: {e}")
    
    # Test 3: Share the news
    print(f"\n3. Sharing News Article:")
    try:
        share_data = {
            "news_uid": news_uid,
            "user_uid": "test123",
            "platform": "facebook",  # Test with Facebook
            "shared_at": datetime.now().isoformat()
        }
        
        response = requests.post(f"{BASE_URL}/news/{news_uid}/share", json=share_data)
        if response.status_code == 200:
            result = response.json()
            print("✅ Share tracked successfully")
            print(f"   Platform: {result.get('platform', 'facebook')}")
            print(f"   Message: {result.get('message', 'Success')}")
        else:
            print(f"❌ Share tracking failed: {response.text}")
    except Exception as e:
        print(f"❌ Error tracking share: {e}")
    
    # Test 4: Add a reaction (like)
    print(f"\n4. Adding Reaction (Like):")
    try:
        reaction_data = {
            "news_uid": news_uid,
            "user_uid": "test123",
            "reaction_type": "like",
            "reacted_at": datetime.now().isoformat()
        }
        
        response = requests.post(f"{BASE_URL}/news/{news_uid}/react", json=reaction_data)
        if response.status_code == 200:
            result = response.json()
            print("✅ Reaction added successfully")
            print(f"   Reaction: {result.get('reaction_type', 'like')}")
            print(f"   Message: {result.get('message', 'Success')}")
        else:
            print(f"❌ Reaction failed: {response.text}")
    except Exception as e:
        print(f"❌ Error adding reaction: {e}")
    
    # Test 5: Add a comment
    print(f"\n5. Adding Comment:")
    try:
        comment_data = {
            "news_uid": news_uid,
            "user_uid": "test123",
            "content": "This is a test comment from the sharing system test!",
            "commented_at": datetime.now().isoformat()
        }
        
        response = requests.post(f"{BASE_URL}/news/{news_uid}/comment", json=comment_data)
        if response.status_code == 200:
            result = response.json()
            print("✅ Comment added successfully")
            print(f"   Comment ID: {result.get('comment_id', 'N/A')}")
            print(f"   Message: {result.get('message', 'Success')}")
        else:
            print(f"❌ Comment failed: {response.text}")
    except Exception as e:
        print(f"❌ Error adding comment: {e}")
    
    # Test 6: Check updated article stats
    print(f"\n6. Checking Updated Article Stats:")
    try:
        response = requests.get(f"{BASE_URL}/news/{news_uid}")
        if response.status_code == 200:
            article = response.json()
            print("✅ Article stats updated:")
            print(f"   👁️ Views: {article.get('views_count', 0)}")
            print(f"   ❤️ Likes: {article.get('likes_count', 0)}")
            print(f"   📤 Shares: {article.get('shares_count', 0)}")
            print(f"   💬 Comments: {article.get('comments_count', 0)}")
        else:
            print(f"❌ Failed to get updated stats: {response.text}")
    except Exception as e:
        print(f"❌ Error getting stats: {e}")
    
    # Test 7: Get engagement summary
    print(f"\n7. Getting Engagement Summary:")
    try:
        response = requests.get(f"{BASE_URL}/news/{news_uid}/engagement")
        if response.status_code == 200:
            engagement = response.json()
            print("✅ Engagement summary:")
            print(f"   Total interactions: {engagement.get('total_interactions', 0)}")
            print(f"   Recent views: {engagement.get('recent_views', 0)}")
            print(f"   Recent shares: {engagement.get('recent_shares', 0)}")
            print(f"   Recent reactions: {engagement.get('recent_reactions', 0)}")
        else:
            print(f"❌ Failed to get engagement: {response.text}")
    except Exception as e:
        print(f"❌ Error getting engagement: {e}")
    
    print(f"\n🎉 Sharing & Engagement Test Complete!")
    print(f"\n📋 What We Tested:")
    print("   ✅ View tracking")
    print("   ✅ Share tracking")
    print("   ✅ Reaction system")
    print("   ✅ Comment system")
    print("   ✅ Updated counters")
    print("   ✅ Engagement summary")

def create_sharing_frontend():
    """Create a simple frontend with sharing buttons"""
    print(f"\n🌐 **Creating Sharing Frontend**")
    print("=" * 40)
    
    frontend_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>News Sharing Demo</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .news-article { border: 1px solid #ddd; padding: 20px; margin-bottom: 20px; border-radius: 8px; }
        .stats { display: flex; gap: 20px; margin: 15px 0; }
        .stat { display: flex; align-items: center; gap: 5px; }
        .sharing-buttons { display: flex; gap: 10px; margin: 15px 0; }
        .share-btn { padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; color: white; }
        .facebook { background: #1877f2; }
        .twitter { background: #1da1f2; }
        .whatsapp { background: #25d366; }
        .linkedin { background: #0077b5; }
        .like-btn { background: #e74c3c; }
        .comment-btn { background: #3498db; }
        .message { padding: 10px; margin: 10px 0; border-radius: 4px; }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <h1>📰 News Sharing Demo</h1>
    <div id="news-container">
        <p>Loading news articles...</p>
    </div>

    <script>
        const API_BASE = 'http://localhost:8001';
        let currentArticle = null;

        async function loadNews() {
            try {
                const response = await fetch(`${API_BASE}/news`);
                const data = await response.json();
                
                if (data.news && data.news.length > 0) {
                    currentArticle = data.news[0];
                    displayArticle(currentArticle);
                } else {
                    document.getElementById('news-container').innerHTML = '<p>No news articles found</p>';
                }
            } catch (error) {
                showMessage('Error loading news: ' + error.message, 'error');
            }
        }

        function displayArticle(article) {
            const container = document.getElementById('news-container');
            container.innerHTML = `
                <div class="news-article">
                    <h2>${article.title}</h2>
                    <p>${article.summary || 'No summary available'}</p>
                    
                    <div class="stats">
                        <div class="stat">👁️ <span id="views">${article.views_count || 0}</span> views</div>
                        <div class="stat">❤️ <span id="likes">${article.likes_count || 0}</span> likes</div>
                        <div class="stat">📤 <span id="shares">${article.shares_count || 0}</span> shares</div>
                        <div class="stat">💬 <span id="comments">${article.comments_count || 0}</span> comments</div>
                    </div>
                    
                    <div class="sharing-buttons">
                        <button class="share-btn facebook" onclick="shareArticle('facebook')">📘 Facebook</button>
                        <button class="share-btn twitter" onclick="shareArticle('twitter')">🐦 Twitter</button>
                        <button class="share-btn whatsapp" onclick="shareArticle('whatsapp')">💬 WhatsApp</button>
                        <button class="share-btn linkedin" onclick="shareArticle('linkedin')">💼 LinkedIn</button>
                    </div>
                    
                    <div class="sharing-buttons">
                        <button class="like-btn share-btn" onclick="likeArticle()">❤️ Like</button>
                        <button class="comment-btn share-btn" onclick="addComment()">💬 Comment</button>
                        <button class="share-btn" style="background: #95a5a6;" onclick="trackView()">👁️ View</button>
                    </div>
                </div>
            `;
        }

        async function shareArticle(platform) {
            if (!currentArticle) return;
            
            try {
                const response = await fetch(`${API_BASE}/news/${currentArticle.news_uid}/share`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        news_uid: currentArticle.news_uid,
                        user_uid: 'test123',
                        platform: platform,
                        shared_at: new Date().toISOString()
                    })
                });
                
                if (response.ok) {
                    showMessage(`Shared to ${platform} successfully!`, 'success');
                    updateStats();
                } else {
                    showMessage(`Share failed: ${await response.text()}`, 'error');
                }
            } catch (error) {
                showMessage('Share error: ' + error.message, 'error');
            }
        }

        async function likeArticle() {
            if (!currentArticle) return;
            
            try {
                const response = await fetch(`${API_BASE}/news/${currentArticle.news_uid}/react`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        news_uid: currentArticle.news_uid,
                        user_uid: 'test123',
                        reaction_type: 'like',
                        reacted_at: new Date().toISOString()
                    })
                });
                
                if (response.ok) {
                    showMessage('Article liked!', 'success');
                    updateStats();
                } else {
                    showMessage('Like failed: ' + await response.text(), 'error');
                }
            } catch (error) {
                showMessage('Like error: ' + error.message, 'error');
            }
        }

        async function addComment() {
            const comment = prompt('Enter your comment:');
            if (!comment || !currentArticle) return;
            
            try {
                const response = await fetch(`${API_BASE}/news/${currentArticle.news_uid}/comment`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        news_uid: currentArticle.news_uid,
                        user_uid: 'test123',
                        content: comment,
                        commented_at: new Date().toISOString()
                    })
                });
                
                if (response.ok) {
                    showMessage('Comment added!', 'success');
                    updateStats();
                } else {
                    showMessage('Comment failed: ' + await response.text(), 'error');
                }
            } catch (error) {
                showMessage('Comment error: ' + error.message, 'error');
            }
        }

        async function trackView() {
            if (!currentArticle) return;
            
            try {
                const response = await fetch(`${API_BASE}/news/${currentArticle.news_uid}/view`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        news_uid: currentArticle.news_uid,
                        user_uid: 'test123',
                        viewed_at: new Date().toISOString()
                    })
                });
                
                if (response.ok) {
                    showMessage('View tracked!', 'success');
                    updateStats();
                } else {
                    showMessage('View tracking failed: ' + await response.text(), 'error');
                }
            } catch (error) {
                showMessage('View error: ' + error.message, 'error');
            }
        }

        async function updateStats() {
            if (!currentArticle) return;
            
            try {
                const response = await fetch(`${API_BASE}/news/${currentArticle.news_uid}`);
                if (response.ok) {
                    const article = await response.json();
                    document.getElementById('views').textContent = article.views_count || 0;
                    document.getElementById('likes').textContent = article.likes_count || 0;
                    document.getElementById('shares').textContent = article.shares_count || 0;
                    document.getElementById('comments').textContent = article.comments_count || 0;
                }
            } catch (error) {
                console.error('Error updating stats:', error);
            }
        }

        function showMessage(message, type) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}`;
            messageDiv.textContent = message;
            document.body.appendChild(messageDiv);
            
            setTimeout(() => messageDiv.remove(), 3000);
        }

        // Load news when page loads
        window.onload = loadNews;
    </script>
</body>
</html>
'''
    
    with open('news_sharing_demo.html', 'w', encoding='utf-8') as f:
        f.write(frontend_html)
    
    print("✅ Created 'news_sharing_demo.html'")
    print("📝 Features:")
    print("   📘 Facebook, Twitter, WhatsApp, LinkedIn sharing")
    print("   ❤️ Like button with reaction tracking")
    print("   💬 Comment system")
    print("   👁️ View tracking")
    print("   📊 Live statistics updates")
    print("🌐 Open: http://localhost:8001/news_sharing_demo.html")

if __name__ == "__main__":
    test_sharing_system()
    create_sharing_frontend()
