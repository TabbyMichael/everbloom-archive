from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from app.models.life_event import LifeEvent
from app.schemas.life_event import LifeEventCreate, LifeEventUpdate

def get_life_events(db: Session, skip: int = 0, limit: int = 100) -> List[LifeEvent]:
    """Get all life events with pagination"""
    return db.query(LifeEvent).offset(skip).limit(limit).all()

def get_life_event(db: Session, event_id: str) -> Optional[LifeEvent]:
    """Get a specific life event by ID"""
    return db.query(LifeEvent).filter(LifeEvent.id == event_id).first()

def get_featured_life_events(db: Session) -> List[LifeEvent]:
    """Get featured life events"""
    return db.query(LifeEvent).filter(LifeEvent.is_featured == True).all()

def get_life_events_by_year(db: Session, year: int) -> List[LifeEvent]:
    """Get life events for a specific year"""
    return db.query(LifeEvent).filter(LifeEvent.event_year == year).all()

def create_life_event(db: Session, event: LifeEventCreate) -> LifeEvent:
    """Create a new life event"""
    db_event = LifeEvent(**event.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def update_life_event(db: Session, event_id: str, event: LifeEventUpdate) -> Optional[LifeEvent]:
    """Update a life event"""
    db_event = get_life_event(db, event_id)
    if db_event:
        update_data = event.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_event, field, value)
        db.commit()
        db.refresh(db_event)
    return db_event

def delete_life_event(db: Session, event_id: str) -> bool:
    """Delete a life event"""
    db_event = get_life_event(db, event_id)
    if db_event:
        db.delete(db_event)
        db.commit()
        return True
    return False

def search_life_events(db: Session, query: str) -> List[LifeEvent]:
    """Search life events by title or description"""
    return db.query(LifeEvent).filter(
        func.or_(
            func.ilike(LifeEvent.title, f"%{query}%"),
            func.ilike(LifeEvent.description, f"%{query}%"),
            func.ilike(LifeEvent.location_name, f"%{query}%")
        )
    ).all()
