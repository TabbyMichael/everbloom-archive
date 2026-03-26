from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
from datetime import datetime
from uuid import UUID

class GalleryBase(BaseModel):
    media_url: HttpUrl = Field(..., description="URL to the media file")
    caption: Optional[str] = None
    is_featured: bool = False
    media_type: str = Field(default="image", regex="^(image|video)$")
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    event_id: Optional[UUID] = None

class GalleryCreate(GalleryBase):
    file_size: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None

class GalleryUpdate(BaseModel):
    caption: Optional[str] = None
    is_featured: Optional[bool] = None
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    event_id: Optional[UUID] = None

class Gallery(GalleryBase):
    id: UUID
    file_size: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    created_at: datetime
    
    class Config:
        orm_mode = True

class GalleryWithEvent(Gallery):
    life_event: Optional["LifeEvent"] = None

# Forward import to avoid circular dependency
from .life_event import LifeEvent
