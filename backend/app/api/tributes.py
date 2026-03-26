from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.crud import tributes as crud
from app.schemas import Tribute, TributeCreate, TributeUpdate, TributePublic
import json
import asyncio
from typing import List

router = APIRouter(prefix="/tributes", tags=["tributes"])

# WebSocket connection manager for real-time candle updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                # Connection closed, remove it
                self.active_connections.remove(connection)

manager = ConnectionManager()

@router.get("/", response_model=List[TributePublic])
def read_tributes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    approved_only: bool = Query(True),
    candles_only: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get tributes with optional filtering"""
    if candles_only:
        return crud.get_candle_tributes(db)
    elif search:
        return crud.search_tributes(db, search, approved_only)
    else:
        return crud.get_tributes(db, skip=skip, limit=limit, approved_only=approved_only)

@router.get("/{tribute_id}", response_model=TributePublic)
def read_tribute(tribute_id: str, db: Session = Depends(get_db)):
    """Get a specific tribute"""
    tribute = crud.get_tribute(db, tribute_id)
    if not tribute or not tribute.approved:
        raise HTTPException(status_code=404, detail="Tribute not found")
    return tribute

@router.post("/", response_model=Tribute)
def create_tribute(tribute: TributeCreate, db: Session = Depends(get_db)):
    """Create a new tribute (requires approval)"""
    return crud.create_tribute(db, tribute)

@router.post("/{tribute_id}/light-candle", response_model=Tribute)
def light_candle(tribute_id: str, db: Session = Depends(get_db)):
    """Light a candle for a tribute"""
    tribute = crud.get_tribute(db, tribute_id)
    if not tribute:
        raise HTTPException(status_code=404, detail="Tribute not found")
    
    # Update candle status
    updated_tribute = crud.update_tribute(db, tribute_id, TributeUpdate(candle_lit=True))
    
    # Broadcast real-time update
    asyncio.create_task(manager.broadcast({
        "type": "candle_lit",
        "tribute_id": tribute_id,
        "author_name": updated_tribute.author_name
    }))
    
    return updated_tribute

@router.get("/admin/pending", response_model=List[Tribute])
def get_pending_tributes(db: Session = Depends(get_db)):
    """Get pending tributes for moderation (admin only)"""
    return crud.get_pending_tributes(db)

@router.post("/{tribute_id}/approve", response_model=Tribute)
def approve_tribute(tribute_id: str, db: Session = Depends(get_db)):
    """Approve a tribute (admin only)"""
    tribute = crud.approve_tribute(db, tribute_id)
    if not tribute:
        raise HTTPException(status_code=404, detail="Tribute not found")
    
    # Broadcast real-time update
    asyncio.create_task(manager.broadcast({
        "type": "tribute_approved",
        "tribute_id": tribute_id,
        "author_name": tribute.author_name
    }))
    
    return tribute

@router.put("/{tribute_id}", response_model=Tribute)
def update_tribute(tribute_id: str, tribute: TributeUpdate, db: Session = Depends(get_db)):
    """Update a tribute (admin only)"""
    db_tribute = crud.update_tribute(db, tribute_id, tribute)
    if not db_tribute:
        raise HTTPException(status_code=404, detail="Tribute not found")
    return db_tribute

@router.delete("/{tribute_id}")
def delete_tribute(tribute_id: str, db: Session = Depends(get_db)):
    """Delete a tribute (admin only)"""
    if not crud.delete_tribute(db, tribute_id):
        raise HTTPException(status_code=404, detail="Tribute not found")
    return {"message": "Tribute deleted successfully"}

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
