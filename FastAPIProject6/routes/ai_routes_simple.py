"""
Simple AI Routes for Testing
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from typing import Dict, Optional
from datetime import datetime
import csv
import io

router = APIRouter()

@router.get("/test-ai")
async def test_ai():
    """
    Test AI endpoint without authentication
    """
    return {
        "success": True,
        "message": "AI routes are working!",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/supported-languages")
async def get_supported_languages():
    """
    Get list of supported languages for AI analysis
    """
    return {
        "success": True,
        "data": {
            "languages": [
                {"code": "en", "name": "English"},
                {"code": "te", "name": "Telugu"},
                {"code": "hi", "name": "Hindi"}
            ]
        }
    }

@router.get("/csv-template")
async def download_csv_template():
    """
    Download CSV template for batch analysis
    """
    template_data = [
        {
            "title": "Sample News Title",
            "content": "Sample news content for analysis...",
            "language": "en",
            "author": "Author Name",
            "source": "Source Name"
        }
    ]
    
    # Create CSV content
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["title", "content", "language", "author", "source"])
    writer.writeheader()
    writer.writerows(template_data)
    
    csv_content = output.getvalue()
    output.close()
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=news_analysis_template.csv"}
    )

@router.post("/sentiment-analysis")
async def sentiment_analysis(request: dict):
    """
    Simple sentiment analysis (mock)
    """
    text = request.get("text", "")
    
    # Simple mock sentiment analysis
    if "good" in text.lower() or "great" in text.lower() or "amazing" in text.lower():
        sentiment = "positive"
    elif "bad" in text.lower() or "terrible" in text.lower() or "awful" in text.lower():
        sentiment = "negative"
    else:
        sentiment = "neutral"
    
    return {
        "success": True,
        "sentiment": sentiment,
        "confidence": 0.85,
        "message": f"Sentiment analysis completed: {sentiment}",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/category-suggestion")
async def category_suggestion(request: dict):
    """
    Simple category suggestion (mock)
    """
    text = request.get("text", "")
    
    # Simple mock category suggestion
    if "tech" in text.lower() or "technology" in text.lower():
        category = "Technology"
    elif "sports" in text.lower():
        category = "Sports"
    elif "politics" in text.lower():
        category = "Politics"
    else:
        category = "General"
    
    return {
        "success": True,
        "suggested_category": category,
        "confidence": 0.80,
        "message": f"Category suggestion: {category}",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/fake-news-detection")
async def fake_news_detection(request: dict):
    """
    Simple fake news detection (mock)
    """
    title = request.get("title", "")
    content = request.get("content", "")
    
    # Simple mock fake news detection
    suspicious_words = ["miracle", "breakthrough", "revolutionary", "shocking", "unbelievable"]
    suspicious_count = sum(1 for word in suspicious_words if word in (title + " " + content).lower())
    
    if suspicious_count >= 2:
        is_fake = True
        confidence = 0.75
    else:
        is_fake = False
        confidence = 0.70
    
    return {
        "success": True,
        "is_fake": is_fake,
        "confidence": confidence,
        "credibility_score": 1 - confidence,
        "message": f"Fake news detection: {'LIKELY FAKE' if is_fake else 'LIKELY REAL'}",
        "timestamp": datetime.utcnow().isoformat()
    }
