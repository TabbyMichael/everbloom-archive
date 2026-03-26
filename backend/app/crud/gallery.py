from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from app.models.gallery import Gallery
from app.schemas.gallery import GalleryCreate, GalleryUpdate

def get_gallery_items(db: Session, skip: int = 0, limit: int = 100) -> List[Gallery]:
    """Get all gallery items with pagination"""
    return db.query(Gallery).offset(skip).limit(limit).all()

def get_gallery_item(db: Session, item_id: str) -> Optional[Gallery]:
    """Get a specific gallery item by ID"""
    return db.query(Gallery).filter(Gallery.id == item_id).first()

def get_featured_gallery_items(db: Session) -> List[Gallery]:
    """Get featured gallery items"""
    return db.query(Gallery).filter(Gallery.is_featured == True).all()

def get_gallery_by_event(db: Session, event_id: str) -> List[Gallery]:
    """Get gallery items for a specific life event"""
    return db.query(Gallery).filter(Gallery.event_id == event_id).all()

def get_gallery_by_type(db: Session, media_type: str) -> List[Gallery]:
    """Get gallery items by media type (image/video)"""
    return db.query(Gallery).filter(Gallery.media_type == media_type).all()

def create_gallery_item(db: Session, item: GalleryCreate) -> Gallery:
    """Create a new gallery item"""
    db_item = Gallery(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def update_gallery_item(db: Session, item_id: str, item: GalleryUpdate) -> Optional[Gallery]:
    """Update a gallery item"""
    db_item = get_gallery_item(db, item_id)
    if db_item:
        update_data = item.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_item, field, value)
        db.commit()
        db.refresh(db_item)
    return db_item

def delete_gallery_item(db: Session, item_id: str) -> bool:
    """Delete a gallery item"""
    db_item = get_gallery_item(db, item_id)
    if db_item:
        db.delete(db_item)
        db.commit()
        return True
    return False

def search_gallery(db: Session, query: str) -> List[Gallery]:
    """Search gallery items by title, caption, or description"""
    return db.query(Gallery).filter(
        func.or_(
            func.ilike(Gallery.title, f"%{query}%"),
            func.ilike(Gallery.caption, f"%{query}%"),
            func.ilike(Gallery.description, f"%{query}%")
        )
    ).all()
