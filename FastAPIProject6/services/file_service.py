"""
File Service for Hyperlocal News Application
Handles file operations, validation, and processing
"""

import os
import uuid
from pathlib import Path
from typing import List, Optional, Dict, Any
from PIL import Image
import aiofiles
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class FileService:
    """Service for handling file operations"""
    
    def __init__(self):
        self.upload_dir = Path("uploads")
        self.images_dir = self.upload_dir / "images"
        self.videos_dir = self.upload_dir / "videos"
        self.thumbnails_dir = self.upload_dir / "thumbnails"
        self.temp_dir = self.upload_dir / "temp"
        
        # Create directories
        for directory in [self.upload_dir, self.images_dir, self.videos_dir, self.thumbnails_dir, self.temp_dir]:
            directory.mkdir(exist_ok=True)
    
    def validate_file_type(self, content_type: str, allowed_types: Dict[str, str]) -> Optional[str]:
        """Validate file type and return extension"""
        return allowed_types.get(content_type)
    
    def validate_file_size(self, file_size: int, max_size: int) -> bool:
        """Validate file size"""
        return file_size <= max_size
    
    def generate_unique_filename(self, original_filename: str, extension: str) -> str:
        """Generate unique filename"""
        return f"{uuid.uuid4()}{extension}"
    
    async def save_file(self, file_content: bytes, file_path: Path) -> bool:
        """Save file content to disk"""
        try:
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(file_content)
            return True
        except Exception as e:
            logger.error(f"Failed to save file: {str(e)}")
            return False
    
    async def create_thumbnail(self, image_path: Path, max_size: tuple = (300, 300)) -> Optional[Path]:
        """Create thumbnail for image"""
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                # Create thumbnail
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Save thumbnail
                thumbnail_filename = f"thumb_{image_path.stem}.jpg"
                thumbnail_path = self.thumbnails_dir / thumbnail_filename
                img.save(thumbnail_path, "JPEG", quality=85)
                
                return thumbnail_path
                
        except Exception as e:
            logger.error(f"Failed to create thumbnail: {str(e)}")
            return None
    
    def get_image_info(self, image_path: Path) -> Dict[str, Any]:
        """Get image information"""
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
    
    async def delete_file(self, file_path: Path) -> bool:
        """Delete file from disk"""
        try:
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete file: {str(e)}")
            return False
    
    def get_file_size(self, file_path: Path) -> int:
        """Get file size in bytes"""
        try:
            return file_path.stat().st_size
        except:
            return 0
    
    def file_exists(self, file_path: Path) -> bool:
        """Check if file exists"""
        return file_path.exists()
    
    def get_file_url(self, filename: str, file_type: str) -> str:
        """Get file URL"""
        if file_type == "image":
            return f"/files/images/{filename}"
        elif file_type == "video":
            return f"/files/videos/{filename}"
        elif file_type == "thumbnail":
            return f"/files/thumbnails/{filename}"
        else:
            return f"/files/{filename}"
    
    async def cleanup_temp_files(self, max_age_hours: int = 24) -> int:
        """Clean up temporary files older than specified hours"""
        try:
            cleaned_count = 0
            cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
            
            for file_path in self.temp_dir.glob("*"):
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    cleaned_count += 1
            
            return cleaned_count
        except Exception as e:
            logger.error(f"Failed to cleanup temp files: {str(e)}")
            return 0
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        try:
            stats = {
                "total_files": 0,
                "total_size": 0,
                "images": {"count": 0, "size": 0},
                "videos": {"count": 0, "size": 0},
                "thumbnails": {"count": 0, "size": 0}
            }
            
            # Count and size images
            for file_path in self.images_dir.glob("*"):
                if file_path.is_file():
                    size = file_path.stat().st_size
                    stats["images"]["count"] += 1
                    stats["images"]["size"] += size
                    stats["total_files"] += 1
                    stats["total_size"] += size
            
            # Count and size videos
            for file_path in self.videos_dir.glob("*"):
                if file_path.is_file():
                    size = file_path.stat().st_size
                    stats["videos"]["count"] += 1
                    stats["videos"]["size"] += size
                    stats["total_files"] += 1
                    stats["total_size"] += size
            
            # Count and size thumbnails
            for file_path in self.thumbnails_dir.glob("*"):
                if file_path.is_file():
                    size = file_path.stat().st_size
                    stats["thumbnails"]["count"] += 1
                    stats["thumbnails"]["size"] += size
                    stats["total_files"] += 1
                    stats["total_size"] += size
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get storage stats: {str(e)}")
            return {"error": str(e)}

# Global file service instance
file_service = FileService()
