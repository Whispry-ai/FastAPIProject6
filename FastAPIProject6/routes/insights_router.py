import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import APIRouter, Depends, HTTPException, status, Form, Path
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
import json
import os

from database import get_db
from models.insorts import Insight, InsightPage, InsightShare
from schemas import (
    InsightStoryCreate, 
    InsightStoryOut, 
    InsightShareCreate
)

router = APIRouter(prefix="/insights", tags=["Insights"])


def generate_insight_uid() -> str:
    """Generate a unique 8-character insight UID."""
    return str(uuid.uuid4())[:8].upper()


def _create_insight_with_pages(
    db: Session,
    insight_uid: str,
    title: str,
    category_name: str,
    cover_image_url: Optional[str],
    pages: List
):
    """Create Insight and its pages in a single transaction."""
    db_insight = Insight(
        insight_uid=insight_uid,
        title=title,
        cover_image_url=cover_image_url,
        category_name=category_name
    )
    db.add(db_insight)
    db.flush()

    for page in pages:
        # Handle Pydantic models - use getattr with default None
        if hasattr(page, 'page_number'):
            page_number = page.page_number
            title_val = page.title
            content_val = page.content
            image_url_val = page.image_url
            video_url_val = page.video_url
        else:
            # Handle plain dicts
            page_number = page.get('page_number')
            title_val = page.get('title')
            content_val = page.get('content')
            image_url_val = page.get('image_url')
            video_url_val = page.get('video_url')

        db_page = InsightPage(
            insight_id=db_insight.id,
            page_number=page_number,
            title=title_val,
            content=content_val,
            image_url=image_url_val,
            video_url=video_url_val
        )
        db.add(db_page)

    db.commit()
    db.refresh(db_insight)
    return db_insight


@router.get("/", response_model=List[InsightStoryOut])
def list_insights(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Get all insights with pagination.
    """
    insights = db.query(Insight).order_by(Insight.id.desc()).offset(offset).limit(limit).all()
    return insights


@router.post("/", response_model=InsightStoryOut, status_code=status.HTTP_201_CREATED)
def create_insight_story(
    insight_data: InsightStoryCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new insight story with its pages.
    """
    # Determine final UID
    final_insight_uid = insight_data.insight_uid or generate_insight_uid()

    # If client supplied a UID, enforce uniqueness
    if insight_data.insight_uid:
        exists = db.query(Insight).filter(Insight.insight_uid == final_insight_uid).first()
        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Insight already exists"
            )
    else:
        # No UID supplied: avoid duplicates by title + category
        exists = db.query(Insight).filter(
            Insight.title == insight_data.title,
            Insight.category_name == insight_data.category_name
        ).first()
        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Insight already exists"
            )

    # Create using helper
    return _create_insight_with_pages(
        db=db,
        insight_uid=final_insight_uid,
        title=insight_data.title,
        category_name=insight_data.category_name,
        cover_image_url=insight_data.cover_image_url,
        pages=insight_data.pages
    )


@router.post("/create", response_model=InsightStoryOut, status_code=status.HTTP_201_CREATED)
async def create_insight_story_with_urls(
    insight_uid: Optional[str] = Form(None),
    title: str = Form(...),
    category_name: str = Form(...),
    cover_image_url: Optional[str] = Form(None),
    pages_json: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Create a new insight story with image URLs only.
    
    This endpoint accepts form data with:
    - insight_uid: Optional unique identifier for the insight (auto-generated if not provided)
    - title: Title of the insight story
    - category_name: Category name
    - cover_image_url: Optional URL for cover image
    - pages_json: JSON string containing page data with image URLs
    """
    try:
        # Determine final UID
        final_insight_uid = insight_uid or generate_insight_uid()
        
        # If client supplied a UID, enforce uniqueness
        if insight_uid:
            existing_insight = db.query(Insight).filter(Insight.insight_uid == final_insight_uid).first()
            if existing_insight:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Insight already exists"
                )
        else:
            # No UID supplied: avoid duplicates by title + category
            existing_insight = db.query(Insight).filter(
                Insight.title == title,
                Insight.category_name == category_name
            ).first()
            if existing_insight:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Insight already exists"
                )
        
        # Parse pages JSON
        try:
            pages_data = json.loads(pages_json)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON format for pages"
            )
        
        # Validate pages have image URLs
        prepared_pages = []
        for page_data in pages_data:
            page_copy = dict(page_data)
            if not page_copy.get('image_url'):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Page {len(prepared_pages) + 1} must have an image_url"
                )
            prepared_pages.append(page_copy)

        # Create using helper
        return _create_insight_with_pages(
            db=db,
            insight_uid=final_insight_uid,
            title=title,
            category_name=category_name,
            cover_image_url=cover_image_url,
            pages=prepared_pages
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create insight: {str(e)}"
        )


@router.get("/{category_name}", response_model=List[InsightStoryOut])
def get_insights_by_category(
    category_name: str,
    db: Session = Depends(get_db)
):
    """
    Get all insights in a given category (for grid view).
    """
    insights = db.query(Insight).filter(
        Insight.category_name == category_name
    ).all()
    
    return insights



@router.patch("/story/{insight_uid}", response_model=InsightStoryOut)
def update_insight_story(
    insight_uid: str,
    insight_data: InsightStoryCreate,
    db: Session = Depends(get_db)
):
    """
    Update an existing insight story.
    Deletes old pages and replaces them with new page data.
    """
    # Find the existing insight
    db_insight = db.query(Insight).filter(
        Insight.insight_uid == insight_uid
    ).first()
    
    if not db_insight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insight not found"
        )
    
    # Update insight details (don't update insight_uid if provided)
    db_insight.title = insight_data.title
    db_insight.cover_image_url = insight_data.cover_image_url
    db_insight.category_name = insight_data.category_name
    
    # Only update insight_uid if provided and different
    if insight_data.insight_uid and insight_data.insight_uid != db_insight.insight_uid:
        # Check if new UID already exists
        existing_insight = db.query(Insight).filter(
            Insight.insight_uid == insight_data.insight_uid
        ).first()
        
        if existing_insight:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insight with this UID already exists"
            )
        
        db_insight.insight_uid = insight_data.insight_uid
    
    # Delete existing pages using insight_id (foreign key)
    db.query(InsightPage).filter(
        InsightPage.insight_id == db_insight.id
    ).delete()
    
    # Create new pages
    for page_data in insight_data.pages:
        db_page = InsightPage(
            insight_id=db_insight.id,
            page_number=page_data.page_number,
            title=page_data.title,
            content=page_data.content,
            image_url=page_data.image_url,
            video_url=page_data.video_url
        )
        db.add(db_page)
    
    db.commit()
    db.refresh(db_insight)
    
    # Get the updated pages for response
    pages = db.query(InsightPage).filter(
        InsightPage.insight_id == db_insight.id
    ).order_by(InsightPage.page_number).all()
    
    db_insight.pages = pages
    
    return db_insight



@router.post("/share")
def share_insight(
    share_data: InsightShareCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new record in the insight_shares table.
    """
    # Verify that the insight exists
    insight = db.query(Insight).filter(
        Insight.insight_uid == share_data.insight_uid
    ).first()
    
    if not insight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insight not found"
        )
    
    # Create the share record
    db_share = InsightShare(
        insight_uid=share_data.insight_uid,
        user_uid=share_data.user_uid,
        platform=share_data.platform
    )
    
    db.add(db_share)
    db.commit()
    
    return {"message": "Insight shared successfully"}


@router.post("/share/{insight_id}")
def share_insight_by_id(
    insight_id: int,
    user_uid: str = Form(...),
    platform: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Create a new record in the insight_shares table using insight ID.
    """
    # Verify that the insight exists
    insight = db.query(Insight).filter(
        Insight.id == insight_id
    ).first()
    
    if not insight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insight not found"
        )
    
    # Create the share record
    db_share = InsightShare(
        insight_uid=insight.insight_uid,
        user_uid=user_uid,
        platform=platform
    )
    
    db.add(db_share)
    db.commit()
    
    return {"message": "Insight shared successfully"}


@router.get("/uid/{insight_uid}", response_model=InsightStoryOut)
def get_insight_story_by_uid(
    insight_uid: str,
    db: Session = Depends(get_db)
):
    """
    Get a single insight story by insight_uid with its pages sorted by page_number.
    """
    insight = db.query(Insight).filter(
        Insight.insight_uid == insight_uid
    ).first()
    
    if not insight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insight not found"
        )
    
    # Get pages sorted by page_number
    pages = db.query(InsightPage).filter(
        InsightPage.insight_id == insight.id
    ).order_by(InsightPage.page_number).all()
    
    # Add pages to insight object for response
    insight.pages = pages
    
    return insight


@router.delete("/uid/{insight_uid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_insight_story_by_uid(
    insight_uid: str,
    db: Session = Depends(get_db)
):
    """
    Delete an insight by insight_uid and its associated pages (via cascading delete).
    """
    insight = db.query(Insight).filter(
        Insight.insight_uid == insight_uid
    ).first()
    
    if not insight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insight not found"
        )
    
    db.delete(insight)
    db.commit()
    
    return None

