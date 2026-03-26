from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.crud import gallery as crud
from app.schemas import Gallery, GalleryCreate, GalleryUpdate
from app.core.config import settings
import os
import uuid
from fastapi.responses import FileResponse

router = APIRouter(prefix="/gallery", tags=["gallery"])

@router.get("/", response_model=List[Gallery])
def read_gallery_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    featured: Optional[bool] = Query(None),
    media_type: Optional[str] = Query(None, regex="^(image|video)$"),
    event_id: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get gallery items with optional filtering"""
    if featured:
        return crud.get_featured_gallery_items(db)
    elif media_type:
        return crud.get_gallery_by_type(db, media_type)
    elif event_id:
        return crud.get_gallery_by_event(db, event_id)
    elif search:
        return crud.search_gallery(db, search)
    else:
        return crud.get_gallery_items(db, skip=skip, limit=limit)

@router.get("/{item_id}", response_model=Gallery)
def read_gallery_item(item_id: str, db: Session = Depends(get_db)):
    """Get a specific gallery item"""
    item = crud.get_gallery_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Gallery item not found")
    return item

@router.post("/", response_model=Gallery)
async def create_gallery_item(
    title: Optional[str] = None,
    caption: Optional[str] = None,
    description: Optional[str] = None,
    is_featured: bool = False,
    media_type: str = "image",
    event_id: Optional[str] = None,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a new gallery item"""
    
    # Validate file
    if file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large")
    
    # Create upload directory if it doesn't exist
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Create gallery item
    item_data = GalleryCreate(
        media_url=f"/uploads/{unique_filename}",
        title=title,
        caption=caption,
        description=description,
        is_featured=is_featured,
        media_type=media_type,
        event_id=event_id,
        file_size=file.size
    )
    
    return crud.create_gallery_item(db, item_data)

@router.put("/{item_id}", response_model=Gallery)
def update_gallery_item(item_id: str, item: GalleryUpdate, db: Session = Depends(get_db)):
    """Update a gallery item"""
    db_item = crud.update_gallery_item(db, item_id, item)
    if not db_item:
        raise HTTPException(status_code=404, detail="Gallery item not found")
    return db_item

@router.delete("/{item_id}")
def delete_gallery_item(item_id: str, db: Session = Depends(get_db)):
    """Delete a gallery item"""
    # Get item to delete file
    item = crud.get_gallery_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Gallery item not found")
    
    # Delete file if it exists
    if item.media_url.startswith("/uploads/"):
        file_path = os.path.join(settings.UPLOAD_DIR, os.path.basename(item.media_url))
        if os.path.exists(file_path):
            os.remove(file_path)
    
    # Delete from database
    if not crud.delete_gallery_item(db, item_id):
        raise HTTPException(status_code=404, detail="Gallery item not found")
    
    return {"message": "Gallery item deleted successfully"}

@router.get("/uploads/{filename}")
def get_uploaded_file(filename: str):
    """Serve uploaded files"""
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(file_path)
