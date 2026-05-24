"""
Fixed File Upload Routes for Hyperlocal News Application
Handles image and video uploads with validation and processing
"""

import os
import uuid
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from PIL import Image
import logging

from database import get_db
from auth.dependencies import get_current_user, require_role
from models.user import User
from schemas import UserRole

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/files", tags=["File Upload"])

# Allowed file types
ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png", 
    "image/gif": ".gif",
    "image/webp": ".webp"
}

ALLOWED_VIDEO_TYPES = {
    "video/mp4": ".mp4",
    "video/avi": ".avi",
    "video/mov": ".mov",
    "video/wmv": ".wmv"
}

# File size limits (in bytes)
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100MB

# Upload directories
UPLOAD_DIR = Path("uploads")
IMAGES_DIR = UPLOAD_DIR / "images"
VIDEOS_DIR = UPLOAD_DIR / "videos"
THUMBNAILS_DIR = UPLOAD_DIR / "thumbnails"

# Create directories if they don't exist
for directory in [UPLOAD_DIR, IMAGES_DIR, VIDEOS_DIR, THUMBNAILS_DIR]:
    directory.mkdir(exist_ok=True)

@router.post("/upload/image")
async def upload_image(
    file: UploadFile = File(...),
    category: str = Query("news", description="Image category: news, profile, advertisement"),
    resize: bool = Query(True, description="Resize image to optimize"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload an image file with validation and processing
    """
    try:
        # Validate file type
        if file.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported image type. Allowed types: {list(ALLOWED_IMAGE_TYPES.keys())}"
            )
        
        # Validate file size
        content = await file.read()
        file_size = len(content)
        
        if file_size > MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {MAX_IMAGE_SIZE // (1024*1024)}MB"
            )
        
        # Generate unique filename
        file_extension = ALLOWED_IMAGE_TYPES[file.content_type]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = IMAGES_DIR / unique_filename
        
        # Save file using regular file operations
        with open(file_path, 'wb') as f:
            f.write(content)
        
        # Process image if needed
        thumbnail_path = None
        if resize:
            thumbnail_path = create_thumbnail(file_path, THUMBNAILS_DIR)
        
        # Get image dimensions
        image_info = get_image_info(file_path)
        
        return {
            "success": True,
            "message": "Image uploaded successfully",
            "file": {
                "id": unique_filename,
                "filename": file.filename,
                "size": file_size,
                "type": file.content_type,
                "category": category,
                "url": f"/files/images/{unique_filename}",
                "thumbnail_url": f"/files/thumbnails/{Path(thumbnail_path).name}" if thumbnail_path else None,
                "dimensions": image_info
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/images/{filename}")
async def get_image(filename: str):
    """
    Serve uploaded images
    """
    try:
        file_path = IMAGES_DIR / filename
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Image not found")
        
        # Determine content type
        content_type = None
        for mime_type, ext in ALLOWED_IMAGE_TYPES.items():
            if filename.endswith(ext):
                content_type = mime_type
                break
        
        if not content_type:
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        # Read and return file
        with open(file_path, 'rb') as f:
            content = f.read()
        
        return JSONResponse(
            content=content,
            media_type=content_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to serve image: {str(e)}")

def create_thumbnail(image_path: Path, thumbnail_dir: Path, max_size: tuple = (300, 300)) -> Path:
    """
    Create a thumbnail for an image
    """
    try:
        # Open image
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # Create thumbnail
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save thumbnail
            thumbnail_filename = f"thumb_{image_path.stem}.jpg"
            thumbnail_path = thumbnail_dir / thumbnail_filename
            img.save(thumbnail_path, "JPEG", quality=85)
            
            return thumbnail_path
            
    except Exception as e:
        logger.error(f"Failed to create thumbnail: {str(e)}")
        return None

def get_image_info(image_path: Path) -> dict:
    """
    Get image information
    """
    try:
        with Image.open(image_path) as img:
            return {
                "width": img.width,
                "height": img.height,
                "format": img.format,
                "mode": img.mode
            }
    except Exception as e:
        logger.error(f"Failed to get image info: {str(e)}")
        return {}
