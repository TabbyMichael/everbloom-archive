from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.crud import life_events as crud
from app.schemas import LifeEvent, LifeEventCreate, LifeEventUpdate, LifeEventWithGallery

router = APIRouter(prefix="/life-events", tags=["life-events"])

@router.get("/", response_model=List[LifeEvent])
def read_life_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    featured: Optional[bool] = Query(None),
    year: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get life events with optional filtering"""
    if featured:
        return crud.get_featured_life_events(db)
    elif year:
        return crud.get_life_events_by_year(db, year)
    elif search:
        return crud.search_life_events(db, search)
    else:
        return crud.get_life_events(db, skip=skip, limit=limit)

@router.get("/{event_id}", response_model=LifeEventWithGallery)
def read_life_event(event_id: str, db: Session = Depends(get_db)):
    """Get a specific life event with gallery items"""
    event = crud.get_life_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Life event not found")
    return event

@router.post("/", response_model=LifeEvent)
def create_life_event(event: LifeEventCreate, db: Session = Depends(get_db)):
    """Create a new life event"""
    return crud.create_life_event(db, event)

@router.put("/{event_id}", response_model=LifeEvent)
def update_life_event(event_id: str, event: LifeEventUpdate, db: Session = Depends(get_db)):
    """Update a life event"""
    db_event = crud.update_life_event(db, event_id, event)
    if not db_event:
        raise HTTPException(status_code=404, detail="Life event not found")
    return db_event

@router.delete("/{event_id}")
def delete_life_event(event_id: str, db: Session = Depends(get_db)):
    """Delete a life event"""
    if not crud.delete_life_event(db, event_id):
        raise HTTPException(status_code=404, detail="Life event not found")
    return {"message": "Life event deleted successfully"}
