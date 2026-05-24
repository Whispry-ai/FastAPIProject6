#!/usr/bin/env python3
"""
Check current endpoints and identify missing ones
"""

import requests
import json
from collections import defaultdict

BASE_URL = "http://localhost:8001"

def check_server():
    """Check if server is running"""
    try:
        response = requests.get(BASE_URL, timeout=5)
        return response.status_code == 200
    except:
        return False

def get_openapi_docs():
    """Get OpenAPI documentation to see all endpoints"""
    try:
        response = requests.get(f"{BASE_URL}/openapi.json")
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def analyze_endpoints():
    """Analyze current endpoints and identify missing ones"""
    print("🔍 **Endpoint Analysis**")
    print("=" * 60)
    
    if not check_server():
        print("❌ Server is not running")
        return
    
    print("✅ Server is running")
    
    # Get OpenAPI docs
    openapi = get_openapi_docs()
    if not openapi:
        print("❌ Cannot get API documentation")
        return
    
    # Extract current endpoints
    current_endpoints = []
    paths = openapi.get("paths", {})
    
    for path, methods in paths.items():
        for method, details in methods.items():
            if method.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                tags = details.get("tags", [])
                operation_id = details.get("operationId", "")
                summary = details.get("summary", "")
                
                current_endpoints.append({
                    "path": path,
                    "method": method.upper(),
                    "tags": tags,
                    "summary": summary,
                    "operation_id": operation_id
                })
    
    print(f"\n📊 **Current Endpoints: {len(current_endpoints)}**")
    
    # Group by tags
    by_tags = defaultdict(list)
    for endpoint in current_endpoints:
        for tag in endpoint["tags"]:
            by_tags[tag].append(endpoint)
    
    for tag, endpoints in sorted(by_tags.items()):
        print(f"\n🏷️  {tag} ({len(endpoints)} endpoints):")
        for ep in endpoints:
            print(f"  {ep['method']} {ep['path']}")
    
    # Identify missing critical endpoints
    missing_endpoints = identify_missing_endpoints(current_endpoints)
    
    print(f"\n🚨 **Missing Critical Endpoints: {len(missing_endpoints)}**")
    for missing in missing_endpoints:
        print(f"  ❌ {missing['method']} {missing['path']} - {missing['description']}")
    
    return current_endpoints, missing_endpoints

def identify_missing_endpoints(current_endpoints):
    """Identify missing critical endpoints"""
    current_paths = {f"{ep['method']} {ep['path']}" for ep in current_endpoints}
    
    missing = [
        {
            "method": "GET",
            "path": "/health",
            "description": "Health check endpoint"
        },
        {
            "method": "GET", 
            "path": "/stats",
            "description": "Application statistics"
        },
        {
            "method": "GET",
            "path": "/news/categories",
            "description": "Get all news categories"
        },
        {
            "method": "GET",
            "path": "/news/trending",
            "description": "Get trending news"
        },
        {
            "method": "GET",
            "path": "/news/recommended",
            "description": "Get recommended news for user"
        },
        {
            "method": "POST",
            "path": "/news/{news_uid}/bookmark",
            "description": "Bookmark news article"
        },
        {
            "method": "DELETE",
            "path": "/news/{news_uid}/bookmark",
            "description": "Remove bookmark"
        },
        {
            "method": "GET",
            "path": "/user/bookmarks",
            "description": "Get user bookmarks"
        },
        {
            "method": "POST",
            "path": "/news/{news_uid}/report",
            "description": "Report inappropriate content"
        },
        {
            "method": "GET",
            "path": "/user/profile",
            "description": "Get user profile"
        },
        {
            "method": "PUT",
            "path": "/user/profile",
            "description": "Update user profile"
        },
        {
            "method": "GET",
            "path": "/notifications",
            "description": "Get user notifications"
        },
        {
            "method": "PUT",
            "path": "/notifications/{notification_id}/read",
            "description": "Mark notification as read"
        },
        {
            "method": "DELETE",
            "path": "/notifications/{notification_id}",
            "description": "Delete notification"
        },
        {
            "method": "GET",
            "path": "/content/events",
            "description": "Get events"
        },
        {
            "method": "GET",
            "path": "/content/polls",
            "description": "Get polls"
        },
        {
            "method": "POST",
            "path": "/content/polls/{poll_id}/vote",
            "description": "Vote in poll"
        },
        {
            "method": "GET",
            "path": "/content/advertisements",
            "description": "Get advertisements"
        },
        {
            "method": "GET",
            "path": "/location/states",
            "description": "Get all states"
        },
        {
            "method": "GET",
            "path": "/location/states/{state_id}/districts",
            "description": "Get districts in state"
        },
        {
            "method": "GET",
            "path": "/location/districts/{district_id}/cities",
            "description": "Get cities in district"
        },
        {
            "method": "GET",
            "path": "/admin/dashboard",
            "description": "Admin dashboard stats"
        },
        {
            "method": "GET",
            "path": "/admin/users",
            "description": "Get all users (admin)"
        },
        {
            "method": "PUT",
            "path": "/admin/users/{user_uid}/suspend",
            "description": "Suspend user (admin)"
        },
        {
            "method": "GET",
            "path": "/admin/reports",
            "description": "Get content reports (admin)"
        }
    ]
    
    # Filter out existing endpoints
    truly_missing = []
    for missing_ep in missing:
        if f"{missing_ep['method']} {missing_ep['path']}" not in current_paths:
            truly_missing.append(missing_ep)
    
    return truly_missing

if __name__ == "__main__":
    analyze_endpoints()
