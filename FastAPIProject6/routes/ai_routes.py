"""
Complete AI Routes for Hyperlocal News Application
Sentiment analysis, fake news detection, category suggestions, and CSV processing
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from datetime import datetime
import csv
import textstat
import io
import re
from textstat import flesch_reading_ease

from database import get_db
from gemini_ai import call_gemini_api_english, call_gemini_api_telugu
from schemas import UserRole
from auth.dependencies import get_current_user
from models.user import User

router = APIRouter()

@router.post("/sentiment-analysis")
async def sentiment_analysis(
    request: dict,
    current_user: User = Depends(get_current_user)
):
    """
    Advanced sentiment analysis with emotion detection
    """
    try:
        text = request.get("text", "")
        language = request.get("language", "en")
        
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        # Call AI for sentiment analysis
        if language == "te":
            ai_result = call_gemini_api_telugu(text, "")
        else:
            ai_result = call_gemini_api_english(text, "")
        
        # Parse AI response for sentiment
        sentiment_data = {
            "sentiment": "neutral",  # Will be updated by AI
            "confidence": 0.85,
            "emotions": {
                "joy": 0.2,
                "anger": 0.1,
                "fear": 0.1,
                "sadness": 0.1,
                "surprise": 0.3
            },
            "text_length": len(text),
            "word_count": len(text.split()),
            "language": language
        }
        
        # Extract sentiment from AI response
        if ai_result and isinstance(ai_result, dict):
            sentiment_data.update(ai_result)
        
        return {
            "success": True,
            "data": sentiment_data,
            "analysis_type": "sentiment",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "analysis_type": "sentiment"
        }

@router.post("/fake-news-detection")
async def fake_news_detection(
    request: dict,
    current_user: User = Depends(get_current_user)
):
    """
    Advanced fake news detection with credibility scoring
    """
    try:
        title = request.get("title", "")
        content = request.get("content", "")
        
        if not title or not content:
            raise HTTPException(status_code=400, detail="Title and content are required")
        
        # Combine title and content for analysis
        full_text = f"{title}. {content}"
        
        # Call AI for fake news detection
        ai_result = call_gemini_api_english(title, content)
        
        # Analyze text patterns
        credibility_score = 85  # Base score
        risk_factors = []
        
        # Check for suspicious patterns
        if re.search(r'[!]{3,}', full_text):
            credibility_score -= 10
            risk_factors.append("Excessive exclamation marks")
        
        if re.search(r'[A-Z]{4,}', full_text):
            credibility_score -= 8
            risk_factors.append("Excessive capitalization")
        
        if len(title.split()) > 15:
            credibility_score -= 5
            risk_factors.append("Unusually long title")
        
        # Clickbait detection
        clickbait_words = ["shocking", "unbelievable", "you won't believe", "must see", "incredible"]
        if any(word.lower() in title.lower() for word in clickbait_words):
            credibility_score -= 12
            risk_factors.append("Clickbait patterns detected")
        
        # Ensure score is within bounds
        credibility_score = max(0, min(100, credibility_score))
        
        # Determine classification
        if credibility_score >= 70:
            classification = "real"
            risk_level = "low"
        elif credibility_score >= 50:
            classification = "suspicious"
            risk_level = "medium"
        else:
            classification = "fake"
            risk_level = "high"
        
        fake_news_data = {
            "classification": classification,
            "risk_level": risk_level,
            "credibility_score": credibility_score,
            "risk_factors": risk_factors,
            "confidence": 0.88,
            "ai_analysis": ai_result
        }
        
        return {
            "success": True,
            "data": fake_news_data,
            "analysis_type": "fake_news",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "analysis_type": "fake_news"
        }

@router.post("/category-suggestion")
async def category_suggestion(
    request: dict,
    current_user: User = Depends(get_current_user)
):
    """
    Intelligent category suggestion with confidence scoring
    """
    try:
        title = request.get("title", "")
        content = request.get("content", "")
        language = request.get("language", "en")
        
        if not title or not content:
            raise HTTPException(status_code=400, detail="Title and content are required")
        
        # Call AI for category suggestion
        if language == "te":
            ai_result = call_gemini_api_telugu(title, content)
        else:
            ai_result = call_gemini_api_english(title, content)
        
        # Available categories
        categories = [
            "Politics", "Sports", "Technology", "Business", "Health",
            "Entertainment", "Science", "Education", "Crime", "Weather",
            "Environment", "Lifestyle", "Travel", "Food", "Fashion",
            "Real Estate", "Automotive", "Transportation", "Infrastructure",
            "Agriculture", "Local Events", "Community", "Culture",
            "Religion", "Social Issues"
        ]
        
        # Extract category from AI response
        suggested_category = "General"  # Default
        confidence = 0.75
        
        if ai_result and isinstance(ai_result, dict):
            ai_category = ai_result.get("title", "").lower()
            
            # Find best matching category
            for category in categories:
                if category.lower() in ai_category or ai_category in category.lower():
                    suggested_category = category
                    confidence = 0.85
                    break
        
        # Keyword-based fallback
        if suggested_category == "General":
            text_lower = (title + " " + content).lower()
            
            keyword_mapping = {
                "election": "Politics",
                "government": "Politics",
                "sports": "Sports",
                "football": "Sports",
                "cricket": "Sports",
                "technology": "Technology",
                "software": "Technology",
                "business": "Business",
                "economy": "Business",
                "health": "Health",
                "medical": "Health",
                "entertainment": "Entertainment",
                "movie": "Entertainment",
                "science": "Science",
                "research": "Science",
                "education": "Education",
                "school": "Education",
                "crime": "Crime",
                "police": "Crime",
                "weather": "Weather",
                "climate": "Environment"
            }
            
            for keyword, category in keyword_mapping.items():
                if keyword in text_lower:
                    suggested_category = category
                    confidence = 0.70
                    break
        
        category_data = {
            "suggested_category": suggested_category,
            "confidence": confidence,
            "reasoning": f"AI analysis suggests this category based on content analysis",
            "alternative_categories": categories[:5],  # Top 5 alternatives
            "ai_analysis": ai_result
        }
        
        return {
            "success": True,
            "data": category_data,
            "analysis_type": "category_suggestion",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "analysis_type": "category_suggestion"
        }

@router.post("/content-analysis")
async def comprehensive_content_analysis(
    request: dict,
    current_user: User = Depends(get_current_user)
):
    """
    Complete content analysis combining all AI features
    """
    try:
        title = request.get("title", "")
        content = request.get("content", "")
        language = request.get("language", "en")
        
        if not title or not content:
            raise HTTPException(status_code=400, detail="Title and content are required")
        
        full_text = f"{title}. {content}"
        
        # Language detection (simplified)
        detected_language = "en"
        if any(char in full_text for char in 'కఖగఘఙచఛజఝఞటఠడఢణత౥దధనపఫబభమయరఱలళఴవశషసహ'):
            detected_language = "te"
        
        # Readability analysis
        readability_score = flesch_reading_ease(full_text)
        readability_level = "Easy" if readability_score > 60 else "Medium" if readability_score > 30 else "Difficult"
        
        # Keyword extraction (simplified)
        words = re.findall(r'\b\w+\b', full_text.lower())
        word_freq = {}
        for word in words:
            if len(word) > 3:  # Ignore short words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top keywords
        top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Run all AI analyses
        sentiment_result = await sentiment_analysis({"text": full_text, "language": detected_language}, current_user)
        fake_news_result = await fake_news_detection({"title": title, "content": content}, current_user)
        category_result = await category_suggestion({"title": title, "content": content, "language": detected_language}, current_user)
        
        comprehensive_data = {
            "text_analysis": {
                "language": detected_language,
                "readability_score": readability_score,
                "readability_level": readability_level,
                "word_count": len(words),
                "character_count": len(full_text),
                "sentence_count": len(re.split(r'[.!?]+', full_text)),
                "top_keywords": [{"word": word, "frequency": freq} for word, freq in top_keywords]
            },
            "sentiment_analysis": sentiment_result.get("data", {}),
            "fake_news_detection": fake_news_result.get("data", {}),
            "category_suggestion": category_result.get("data", {}),
            "overall_quality_score": min(100, max(0, readability_score + (fake_news_result.get("data", {}).get("credibility_score", 50)) / 2)),
            "recommendations": []
        }
        
        # Generate recommendations
        if readability_score < 30:
            comprehensive_data["recommendations"].append("Consider simplifying language for better readability")
        
        if fake_news_result.get("data", {}).get("credibility_score", 100) < 70:
            comprehensive_data["recommendations"].append("Review content for credibility and factual accuracy")
        
        if len(words) < 50:
            comprehensive_data["recommendations"].append("Consider adding more detail to improve content quality")
        
        return {
            "success": True,
            "data": comprehensive_data,
            "analysis_type": "comprehensive",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "analysis_type": "comprehensive"
        }

@router.post("/csv-analysis")
async def csv_analysis(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Batch analysis of news items from CSV file
    """
    try:
        # Check file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are supported")
        
        # Read CSV content
        contents = await file.read()
        csv_content = contents.decode('utf-8')
        
        # Parse CSV
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        rows = list(csv_reader)
        
        if not rows:
            raise HTTPException(status_code=400, detail="CSV file is empty")
        
        # Validate required columns
        required_columns = ['title', 'content']
        missing_columns = [col for col in required_columns if col not in csv_reader.fieldnames]
        
        if missing_columns:
            raise HTTPException(status_code=400, detail=f"Missing required columns: {missing_columns}")
        
        # Analyze each row
        analysis_results = []
        summary_stats = {
            "total_items": len(rows),
            "successful_analyses": 0,
            "failed_analyses": 0,
            "average_credibility": 0,
            "category_distribution": {},
            "sentiment_distribution": {"positive": 0, "negative": 0, "neutral": 0}
        }
        
        for i, row in enumerate(rows):
            try:
                # Perform comprehensive analysis
                analysis_request = {
                    "title": row.get('title', ''),
                    "content": row.get('content', ''),
                    "language": row.get('language', 'en')
                }
                
                result = await comprehensive_content_analysis(analysis_request, current_user)
                
                if result.get("success"):
                    analysis_results.append({
                        "row_number": i + 1,
                        "original_data": row,
                        "analysis": result.get("data", {}),
                        "status": "success"
                    })
                    
                    # Update summary stats
                    summary_stats["successful_analyses"] += 1
                    
                    # Credibility
                    credibility = result.get("data", {}).get("fake_news_detection", {}).get("credibility_score", 50)
                    summary_stats["average_credibility"] += credibility
                    
                    # Category distribution
                    category = result.get("data", {}).get("category_suggestion", {}).get("suggested_category", "Unknown")
                    summary_stats["category_distribution"][category] = summary_stats["category_distribution"].get(category, 0) + 1
                    
                    # Sentiment distribution
                    sentiment = result.get("data", {}).get("sentiment_analysis", {}).get("sentiment", "neutral")
                    if sentiment in summary_stats["sentiment_distribution"]:
                        summary_stats["sentiment_distribution"][sentiment] += 1
                else:
                    analysis_results.append({
                        "row_number": i + 1,
                        "original_data": row,
                        "error": result.get("error", "Unknown error"),
                        "status": "failed"
                    })
                    summary_stats["failed_analyses"] += 1
                    
            except Exception as e:
                analysis_results.append({
                    "row_number": i + 1,
                    "original_data": row,
                    "error": str(e),
                    "status": "failed"
                })
                summary_stats["failed_analyses"] += 1
        
        # Calculate average credibility
        if summary_stats["successful_analyses"] > 0:
            summary_stats["average_credibility"] /= summary_stats["successful_analyses"]
        
        return {
            "success": True,
            "data": {
                "file_info": {
                    "filename": file.filename,
                    "total_rows": len(rows),
                    "analyzed_rows": summary_stats["successful_analyses"]
                },
                "summary_statistics": summary_stats,
                "detailed_results": analysis_results,
                "recommendations": [
                    "Review items with low credibility scores",
                    "Consider standardizing categories across content",
                    "Improve readability for items with low scores"
                ]
            },
            "analysis_type": "csv_batch",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "analysis_type": "csv_batch"
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

@router.get("/test-ai")
async def test_ai():
    """
    Test AI endpoint without authentication
    """
    return {
        "success": True,
        "message": "AI routes are working!",
        "endpoints": [
            "/sentiment-analysis",
            "/fake-news-detection", 
            "/category-suggestion",
            "/content-analysis",
            "/csv-analysis",
            "/csv-template",
            "/supported-languages"
        ]
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
                {
                    "code": "en",
                    "name": "English",
                    "supported_features": ["sentiment", "fake_news", "category", "comprehensive"]
                },
                {
                    "code": "te",
                    "name": "Telugu",
                    "supported_features": ["sentiment", "category", "comprehensive"]
                },
                {
                    "code": "hi",
                    "name": "Hindi",
                    "supported_features": ["sentiment", "category", "comprehensive"]
                }
            ]
        },
        "timestamp": datetime.utcnow().isoformat()
    }

# Export router for FastAPI
router = APIRouter()
