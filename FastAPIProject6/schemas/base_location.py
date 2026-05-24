"""
Base Location Schemas
Pydantic models for location-related API responses
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

class CategoryOut(BaseModel):
    """Output schema for category"""
    id: int
    name: str
    description: Optional[str] = None

class LanguageCreate(BaseModel):
    """Schema for creating a language"""
    name: str = Field(..., min_length=1, max_length=50)
    code: str = Field(..., min_length=2, max_length=50)

class LanguageOut(BaseModel):
    """Output schema for language"""
    id: int
    name: str
    code: str

class LanguageResponse(BaseModel):
    """Response schema for language list"""
    languages: List[LanguageOut]
    total: int

class StateCreate(BaseModel):
    """Schema for creating a state"""
    name: str = Field(..., min_length=1, max_length=100)
    language_id: Optional[int] = None

class StateOut(BaseModel):
    """Output schema for state"""
    id: int
    name: str
    language_id: Optional[int] = None

class StateLanguageResponse(BaseModel):
    """Response schema for state with language"""
    state: StateOut
    language: Optional[LanguageOut] = None
    message: str

class DistrictCreate(BaseModel):
    """Schema for creating a district"""
    name: str = Field(..., min_length=1, max_length=100)
    state_id: int = Field(..., ge=1)

class DistrictOut(BaseModel):
    """Output schema for district"""
    id: int
    name: str
    state_id: int

class CityCreate(BaseModel):
    """Schema for creating a city"""
    name: str = Field(..., min_length=1, max_length=100)
    state_id: int = Field(..., ge=1)
    district_id: int = Field(..., ge=1)

class CityOut(BaseModel):
    """Output schema for city"""
    id: int
    name: str
    state_id: int
    district_id: int

    model_config = ConfigDict(from_attributes=True)
