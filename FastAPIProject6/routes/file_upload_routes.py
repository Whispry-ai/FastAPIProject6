"""
File Upload Routes for Hyperlocal News Application
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
import aiofiles
import logging

from database import get_db
from auth.dependencies import get_current_user, require_role
from models.user import User
from schemas import UserRole
from services.file_service import FileService

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
        file_size = 0
        content = await file.read()
        file_size = len(content)
        
        if file_size > MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {MAX_IMAGE_SIZE // (1024*1024)}MB"
            )
        
        # Reset file pointer
        await file.seek(0)
        
        # Generate unique filename
        file_extension = ALLOWED_IMAGE_TYPES[file.content_type]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = IMAGES_DIR / unique_filename
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        # Process image if needed
        thumbnail_path = None
        if resize:
            thumbnail_path = await create_thumbnail(file_path, THUMBNAILS_DIR)
        
        # Get image dimensions
        image_info = await get_image_info(file_path)
        
        # Save to database (you might want to create a FileUpload model)
        file_record = {
            "filename": unique_filename,
            "original_filename": file.filename,
            "file_path": str(file_path),
            "thumbnail_path": str(thumbnail_path) if thumbnail_path else None,
            "file_size": file_size,
            "content_type": file.content_type,
            "category": category,
            "uploaded_by": current_user.user_uid,
            "image_info": image_info
        }
        
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

@router.post("/upload/video")
async def upload_video(
    file: UploadFile = File(...),
    category: str = Query("news", description="Video category: news, advertisement"),
    current_user: User = Depends(require_role(UserRole.PUBLISHER)),
    db: Session = Depends(get_db)
):
    """
    Upload a video file with validation
    """
    try:
        # Validate file type
        if file.content_type not in ALLOWED_VIDEO_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported video type. Allowed types: {list(ALLOWED_VIDEO_TYPES.keys())}"
            )
        
        # Validate file size
        file_size = 0
        content = await file.read()
        file_size = len(content)
        
        if file_size > MAX_VIDEO_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {MAX_VIDEO_SIZE // (1024*1024)}MB"
            )
        
        # Reset file pointer
        await file.seek(0)
        
        # Generate unique filename
        file_extension = ALLOWED_VIDEO_TYPES[file.content_type]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = VIDEOS_DIR / unique_filename
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        # Get video info (simplified - you might want to use ffmpeg)
        video_info = {
            "duration": None,  # Would need video processing library
            "resolution": None,
            "format": file.content_type
        }
        
        return {
            "success": True,
            "message": "Video uploaded successfully",
            "file": {
                "id": unique_filename,
                "filename": file.filename,
                "size": file_size,
                "type": file.content_type,
                "category": category,
                "url": f"/files/videos/{unique_filename}",
                "info": video_info
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Video upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.post("/upload/batch")
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
    category: str = Query("news", description="File category"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload multiple files at once
    """
    try:
        if len(files) > 10:  # Limit batch uploads
            raise HTTPException(status_code=400, detail="Maximum 10 files allowed per batch")
        
        results = []
        errors = []
        
        for file in files:
            try:
                if file.content_type in ALLOWED_IMAGE_TYPES:
                    # Handle image upload
                    result = await upload_image(file, category, True, current_user, db)
                    results.append(result["file"])
                elif file.content_type in ALLOWED_VIDEO_TYPES:
                    # Handle video upload
                    result = await upload_video(file, category, current_user, db)
                    results.append(result["file"])
                else:
                    errors.append(f"Unsupported file type: {file.filename}")
                    
            except Exception as e:
                errors.append(f"Failed to upload {file.filename}: {str(e)}")
        
        return {
            "success": True,
            "message": f"Uploaded {len(results)} files successfully",
            "uploaded_files": results,
            "errors": errors
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch upload failed: {str(e)}")

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
        async with aiofiles.open(file_path, 'rb') as f:
            content = await f.read()
        
        return JSONResponse(
            content=content,
            media_type=content_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to serve image: {str(e)}")

@router.get("/videos/{filename}")
async def get_video(filename: str):
    """
    Serve uploaded videos
    """
    try:
        file_path = VIDEOS_DIR / filename
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Video not found")
        
        # Determine content type
        content_type = None
        for mime_type, ext in ALLOWED_VIDEO_TYPES.items():
            if filename.endswith(ext):
                content_type = mime_type
                break
        
        if not content_type:
            raise HTTPException(status_code=400, detail="Invalid video file")
        
        # Read and return file
        async with aiofiles.open(file_path, 'rb') as f:
            content = await f.read()
        
        return JSONResponse(
            content=content,
            media_type=content_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to serve video: {str(e)}")

@router.get("/thumbnails/{filename}")
async def get_thumbnail(filename: str):
    """
    Serve image thumbnails
    """
    try:
        file_path = THUMBNAILS_DIR / filename
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Thumbnail not found")
        
        # Read and return file
        async with aiofiles.open(file_path, 'rb') as f:
            content = await f.read()
        
        return JSONResponse(
            content=content,
            media_type="image/jpeg"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to serve thumbnail: {str(e)}")

@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete an uploaded file
    """
    try:
        # Check if file exists in different directories
        file_path = None
        thumbnail_path = None
        
        # Check images
        image_path = IMAGES_DIR / file_id
        if image_path.exists():
            file_path = image_path
        
        # Check videos
        video_path = VIDEOS_DIR / file_id
        if video_path.exists():
            file_path = video_path
        
        # Check thumbnails
        thumb_path = THUMBNAILS_DIR / file_id
        if thumb_path.exists():
            thumbnail_path = thumb_path
        
        if not file_path:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Delete files
        if file_path:
            file_path.unlink()
        
        if thumbnail_path:
            thumbnail_path.unlink()
        
        return {
            "success": True,
            "message": "File deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")

@router.get("/list")
async def list_user_files(
    category: Optional[str] = Query(None, description="Filter by category"),
    file_type: Optional[str] = Query(None, description="Filter by type: image, video"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List files uploaded by the current user
    """
    try:
        files = []
        
        # List images
        if not file_type or file_type == "image":
            for file_path in IMAGES_DIR.glob("*"):
                if file_path.is_file():
                    files.append({
                        "id": file_path.name,
                        "filename": file_path.name,
                        "type": "image",
                        "size": file_path.stat().st_size,
                        "url": f"/files/images/{file_path.name}",
                        "uploaded_at": file_path.stat().st_mtime
                    })
        
        # List videos
        if not file_type or file_type == "video":
            for file_path in VIDEOS_DIR.glob("*"):
                if file_path.is_file():
                    files.append({
                        "id": file_path.name,
                        "filename": file_path.name,
                        "type": "video",
                        "size": file_path.stat().st_size,
                        "url": f"/files/videos/{file_path.name}",
                        "uploaded_at": file_path.stat().st_mtime
                    })
        
        # Sort by upload time (newest first)
        files.sort(key=lambda x: x["uploaded_at"], reverse=True)
        
        return {
            "success": True,
            "files": files
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")

async def create_thumbnail(image_path: Path, thumbnail_dir: Path, max_size: tuple = (300, 300)) -> Path:
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

async def get_image_info(image_path: Path) -> dict:
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
