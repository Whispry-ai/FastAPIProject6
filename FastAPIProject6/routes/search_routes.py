"""
Search Routes for Hyperlocal News Application
Advanced search with filters, sorting, and pagination
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc, asc
from typing import List, Optional
from datetime import datetime, timedelta

from database import get_db
from models.news import News
from models.content import Advertisement, Event, Poll
from models.user import User
# from schemas import NewsResponse, AdvertisementResponse, EventResponse, PollResponse

router = APIRouter(prefix="/search", tags=["Search"])

@router.get("/news", response_model=dict)
def search_news(
    q: str = Query(..., min_length=1, description="Search query"),
    category_id: Optional[int] = Query(None, description="Filter by category"),
    state_id: Optional[int] = Query(None, description="Filter by state"),
    district_id: Optional[int] = Query(None, description="Filter by district"),
    city_id: Optional[int] = Query(None, description="Filter by city"),
    language_id: Optional[int] = Query(None, description="Filter by language"),
    date_from: Optional[str] = Query(None, description="Filter by date from (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Filter by date to (YYYY-MM-DD)"),
    sort_by: Optional[str] = Query("relevance", description="Sort by: relevance, date, popularity"),
    sort_order: Optional[str] = Query("desc", description="Sort order: asc, desc"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    Search news articles with advanced filters
    """
    try:
        # Build base query
        query = db.query(News).filter(News.is_approved == 1)
        
        # Add text search
        if q:
            search_filter = or_(
                News.title.ilike(f"%{q}%"),
                News.summary.ilike(f"%{q}%")
            )
            query = query.filter(search_filter)
        
        # Add filters
        if category_id:
            query = query.join(News.categories).filter(News.categories.any(id=category_id))
        
        if state_id:
            query = query.filter(News.city.has(districts.has(state_id=state_id)))
        
        if district_id:
            query = query.filter(News.city.has(district_id=district_id))
        
        if city_id:
            query = query.filter(News.city_id == city_id)
        
        if language_id:
            query = query.filter(News.language_id == language_id)
        
        # Add date filters
        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, "%Y-%m-%d")
                query = query.filter(News.created_at >= date_from_obj)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date_from format")
        
        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, "%Y-%m-%d")
                query = query.filter(News.created_at <= date_to_obj)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date_to format")
        
        # Add sorting
        if sort_by == "date":
            order_col = News.created_at
        elif sort_by == "popularity":
            order_col = News.views_count + News.likes_count + News.shares_count
        else:  # relevance
            # Simple relevance: prioritize exact title matches
            if q:
                order_col = News.title.ilike(f"%{q}%").desc()
            else:
                order_col = News.created_at
        
        if sort_order == "asc":
            query = query.order_by(asc(order_col))
        else:
            query = query.order_by(desc(order_col))
        
        # Get total count
        total = query.count()
        
        # Add pagination
        offset = (page - 1) * limit
        results = query.offset(offset).limit(limit).all()
        
        # Format results
        news_items = []
        for news in results:
            news_items.append({
                "id": news.id,
                "news_uid": news.news_uid,
                "title": news.title,
                "summary": news.summary,
                "image_url": news.image_url,
                "created_at": news.created_at.isoformat() if news.created_at else None,
                "views_count": news.views_count or 0,
                "likes_count": news.likes_count or 0,
                "comments_count": news.comments_count or 0,
                "shares_count": news.shares_count or 0,
                "is_breaking": news.is_breaking or False,
                "relevance_score": calculate_relevance_score(news, q) if q else 1.0
            })
        
        return {
            "success": True,
            "data": news_items,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit,
                "has_next": page * limit < total,
                "has_prev": page > 1
            },
            "filters": {
                "query": q,
                "category_id": category_id,
                "state_id": state_id,
                "district_id": district_id,
                "city_id": city_id,
                "language_id": language_id,
                "date_from": date_from,
                "date_to": date_to,
                "sort_by": sort_by,
                "sort_order": sort_order
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/suggestions")
def get_search_suggestions(
    q: str = Query(..., min_length=2, description="Partial search query"),
    limit: int = Query(5, ge=1, le=20, description="Number of suggestions"),
    db: Session = Depends(get_db)
):
    """
    Get search suggestions based on partial query
    """
    try:
        suggestions = []
        
        # Get news title suggestions
        news_suggestions = db.query(News.title).filter(
            and_(
                News.title.ilike(f"%{q}%"),
                News.is_approved == 1
            )
        ).limit(limit).all()
        
        for suggestion in news_suggestions:
            suggestions.append({
                "type": "news",
                "text": suggestion[0],
                "category": "News"
            })
        
        # Get category suggestions (if categories table exists)
        from models.news import Category
        category_suggestions = db.query(Category.name).filter(
            Category.name.ilike(f"%{q}%")
        ).limit(limit // 2).all()
        
        for suggestion in category_suggestions:
            suggestions.append({
                "type": "category",
                "text": suggestion[0],
                "category": "Category"
            })
        
        return {
            "success": True,
            "suggestions": suggestions[:limit]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get suggestions: {str(e)}")

@router.get("/trending")
def get_trending_topics(
    limit: int = Query(10, ge=1, le=50, description="Number of trending topics"),
    time_range: str = Query("24h", description="Time range: 1h, 6h, 24h, 7d"),
    db: Session = Depends(get_db)
):
    """
    Get trending topics based on recent engagement
    """
    try:
        # Calculate time range
        time_mapping = {
            "1h": timedelta(hours=1),
            "6h": timedelta(hours=6),
            "24h": timedelta(hours=24),
            "7d": timedelta(days=7)
        }
        
        if time_range not in time_mapping:
            raise HTTPException(status_code=400, detail="Invalid time_range")
        
        time_threshold = datetime.utcnow() - time_mapping[time_range]
        
        # Get trending news based on engagement
        trending_news = db.query(News).filter(
            and_(
                News.is_approved == 1,
                News.created_at >= time_threshold
            )
        ).order_by(
            desc(
                (News.views_count or 0) + 
                (News.likes_count or 0) + 
                (News.shares_count or 0) + 
                (News.comments_count or 0)
            )
        ).limit(limit).all()
        
        trending_topics = []
        for news in trending_news:
            # Extract keywords from title (simple implementation)
            keywords = extract_keywords(news.title)
            trending_topics.append({
                "title": news.title,
                "summary": news.summary,
                "keywords": keywords,
                "engagement_score": (
                    (news.views_count or 0) + 
                    (news.likes_count or 0) + 
                    (news.shares_count or 0) + 
                    (news.comments_count or 0)
                ),
                "created_at": news.created_at.isoformat() if news.created_at else None,
                "news_uid": news.news_uid
            })
        
        return {
            "success": True,
            "trending_topics": trending_topics,
            "time_range": time_range,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get trending topics: {str(e)}")

def calculate_relevance_score(news: News, query: str) -> float:
    """Calculate relevance score for search ranking"""
    if not query:
        return 1.0
    
    query_lower = query.lower()
    title_lower = news.title.lower()
    summary_lower = news.summary.lower()
    
    score = 0.0
    
    # Exact title match gets highest score
    if query_lower == title_lower:
        score += 1.0
    
    # Title contains query
    if query_lower in title_lower:
        score += 0.8
    
    # Summary contains query
    if query_lower in summary_lower:
        score += 0.6
    
    # Partial matches
    query_words = query_lower.split()
    title_words = title_lower.split()
    summary_words = summary_lower.split()
    
    # Word overlap in title
    title_overlap = len(set(query_words) & set(title_words))
    if query_words:
        score += (title_overlap / len(query_words)) * 0.4
    
    # Word overlap in summary
    summary_overlap = len(set(query_words) & set(summary_words))
    if query_words:
        score += (summary_overlap / len(query_words)) * 0.2
    
    # Engagement boost
    engagement_score = (
        (news.views_count or 0) + 
        (news.likes_count or 0) + 
        (news.shares_count or 0) + 
        (news.comments_count or 0)
    )
    score += min(engagement_score / 1000, 0.2)  # Max 0.2 boost from engagement
    
    return min(score, 1.0)

def extract_keywords(text: str) -> List[str]:
    """Extract keywords from text (simple implementation)"""
    # Remove common words and extract important terms
    common_words = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "is", "was", "are", "were", "be", "been", "have",
        "has", "had", "do", "does", "did", "will", "would", "could", "should"
    }
    
    words = text.lower().split()
    keywords = [word for word in words if word not in common_words and len(word) > 2]
    
    # Return top 5 keywords
    return keywords[:5]
