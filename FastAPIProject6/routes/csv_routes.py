"""
CSV Import/Export Routes for FastAPI Application
"""

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
from auth.dependencies import admin_required, require_role
from io import StringIO
import csv
from typing import Dict, Any, Optional

from database import get_db
from services.csv_service import CSVService
from models.news import News, Category
from schemas import UserRole
from models.user import User

router = APIRouter(prefix="/csv", tags=["CSV"])

@router.post("/import-news", summary="Import news from CSV file")
def import_news_from_csv(
    file: UploadFile = File(..., description="CSV file with news data"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.PUBLISHER))
):
    """
    Import news articles from a CSV file.
    
    - **file**: CSV file containing news data
    - **Required columns**: title, summary, content, language_id, user_uid
    - **Optional columns**: image_url, source_url, source_name, city_id, category_ids
    
    Returns import statistics including success count and any errors.
    """
    try:
        # Read file content
        content = file.file.read().decode('utf-8')
        
        # Import news using CSV service
        result = CSVService.import_news_from_csv(content, db)
        
        return {
            "success": result['success'],
            "message": f"Successfully imported {result['imported_count']} news articles" if result['success'] else "Import failed",
            "imported_count": result['imported_count'],
            "total_rows": result['total_rows'],
            "errors": result['errors'][:10]  # Limit errors to first 10
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File processing error: {str(e)}")

@router.get("/export-news", summary="Export news to CSV")
def export_news_to_csv(
    language_id: Optional[int] = Query(None, description="Filter by language ID"),
    user_uid: Optional[str] = Query(None, description="Filter by user UID"),
    city_id: Optional[int] = Query(None, description="Filter by city ID"),
    limit: int = Query(1000, ge=1, le=10000, description="Maximum number of records to export"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.PUBLISHER))
):
    """
    Export news articles to CSV format.
    
    - **language_id**: Filter by language (optional)
    - **user_uid**: Filter by user (optional)
    - **city_id**: Filter by city (optional)
    - **limit**: Maximum records to export (default: 1000)
    
    Returns CSV file with all news articles matching filters.
    """
    try:
        # Build filters
        filters = {}
        if language_id:
            filters['language_id'] = language_id
        if user_uid:
            filters['user_uid'] = user_uid
        if city_id:
            filters['city_id'] = city_id
        
        # Export news using CSV service
        csv_content = CSVService.export_news_to_csv(db, filters)
        
        # Create streaming response
        output = StringIO(csv_content)
        output.seek(0)
        
        return StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=news_export.csv"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export error: {str(e)}")

@router.get("/export-categories", summary="Export categories to CSV")
def export_categories_to_csv(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.USER))
):
    """
    Export all categories to CSV format.
    
    Returns CSV file with all categories.
    """
    try:
        csv_content = CSVService.export_categories_to_csv(db)
        
        return StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=categories_export.csv"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export error: {str(e)}")

@router.get("/template", summary="Download CSV template")
def get_csv_template():
    """
    Download a CSV template for news import.
    
    Returns a CSV file with proper structure for news import.
    """
    try:
        csv_content = CSVService.generate_csv_template()
        
        return StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=news_template.csv"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Template generation error: {str(e)}")

@router.post("/validate", summary="Validate CSV structure")
def validate_csv_structure(
    file: UploadFile = File(..., description="CSV file to validate"),
    db: Session = Depends(get_db)
):
    """
    Validate CSV file structure without importing data.
    
    - **file**: CSV file to validate
    
    Returns validation results including missing columns and structure analysis.
    """
    try:
        # Read file content
        content = file.file.read().decode('utf-8')
        
        # Validate structure
        validation = CSVService.validate_csv_structure(content)
        
        return {
            "valid": validation['valid'],
            "message": "CSV structure is valid" if validation['valid'] else f"Invalid structure: {validation['error']}",
            "total_rows": validation['total_rows'],
            "found_columns": validation['found_columns'],
            "missing_columns": validation['missing_columns'],
            "unknown_columns": validation['unknown_columns']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")
