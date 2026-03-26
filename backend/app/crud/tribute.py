from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from app.models.tribute import Tribute
from app.schemas.tribute import TributeCreate, TributeUpdate

def get_tributes(db: Session, skip: int = 0, limit: int = 100, approved_only: bool = True) -> List[Tribute]:
    """Get tributes with pagination and approval filter"""
    query = db.query(Tribute)
    if approved_only:
        query = query.filter(Tribute.approved == True)
    return query.offset(skip).limit(limit).all()

def get_tribute(db: Session, tribute_id: str) -> Optional[Tribute]:
    """Get a specific tribute by ID"""
    return db.query(Tribute).filter(Tribute.id == tribute_id).first()

def get_candle_tributes(db: Session) -> List[Tribute]:
    """Get all tributes with candles lit"""
    return db.query(Tribute).filter(
        Tribute.candle_lit == True,
        Tribute.approved == True
    ).all()

def create_tribute(db: Session, tribute: TributeCreate) -> Tribute:
    """Create a new tribute (unapproved by default)"""
    db_tribute = Tribute(**tribute.dict())
    db.add(db_tribute)
    db.commit()
    db.refresh(db_tribute)
    return db_tribute

def update_tribute(db: Session, tribute_id: str, tribute: TributeUpdate) -> Optional[Tribute]:
    """Update a tribute"""
    db_tribute = get_tribute(db, tribute_id)
    if db_tribute:
        update_data = tribute.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_tribute, field, value)
        db.commit()
        db.refresh(db_tribute)
    return db_tribute

def approve_tribute(db: Session, tribute_id: str) -> Optional[Tribute]:
    """Approve a tribute"""
    return update_tribute(db, tribute_id, TributeUpdate(approved=True))

def delete_tribute(db: Session, tribute_id: str) -> bool:
    """Delete a tribute"""
    db_tribute = get_tribute(db, tribute_id)
    if db_tribute:
        db.delete(db_tribute)
        db.commit()
        return True
    return False

def search_tributes(db: Session, query: str, approved_only: bool = True) -> List[Tribute]:
    """Search tributes by author name or message"""
    db_query = db.query(Tribute)
    if approved_only:
        db_query = db_query.filter(Tribute.approved == True)
    
    return db_query.filter(
        func.or_(
            func.ilike(Tribute.author_name, f"%{query}%"),
            func.ilike(Tribute.message, f"%{query}%"),
            func.ilike(Tribute.relation_to_deceased, f"%{query}%")
        )
    ).all()

def get_pending_tributes(db: Session) -> List[Tribute]:
    """Get all pending (unapproved) tributes for moderation"""
    return db.query(Tribute).filter(Tribute.approved == False).all()
