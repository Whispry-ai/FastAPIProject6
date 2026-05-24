"""
Insights Schemas
Pydantic models for insights and analytics
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class InsightStoryCreate(BaseModel):
    """Schema for creating an insight story"""
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1, max_length=50)
    is_featured: bool = Field(default=False)

class InsightStoryOut(BaseModel):
    """Output schema for insight story"""
    id: int
    title: str
    content: str
    category: str
    is_featured: bool
    created_at: datetime

class InsightShareCreate(BaseModel):
    """Schema for creating an insight share"""
    insight_id: int = Field(..., ge=1)
    platform: str = Field(..., min_length=1, max_length=50)
    message: Optional[str] = Field(None, max_length=500)

class InsightStoryResponse(BaseModel):
    """Response schema for insight stories"""
    stories: List[InsightStoryOut]
    total: int
    page: int
    limit: int
