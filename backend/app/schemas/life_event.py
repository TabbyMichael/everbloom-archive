from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

class LifeEventBase(BaseModel):
    event_year: int = Field(..., ge=1900, le=2100)
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    location_name: Optional[str] = None
    coordinates: Optional[tuple[float, float]] = None  # (latitude, longitude)
    is_featured: bool = False

class LifeEventCreate(LifeEventBase):
    pass

class LifeEventUpdate(BaseModel):
    event_year: Optional[int] = Field(None, ge=1900, le=2100)
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    location_name: Optional[str] = None
    coordinates: Optional[tuple[float, float]] = None
    is_featured: Optional[bool] = None

class LifeEvent(LifeEventBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class LifeEventWithGallery(LifeEvent):
    gallery_items: list["Gallery"] = []

# Forward import to avoid circular dependency
from .gallery import Gallery
