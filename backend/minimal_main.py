#!/usr/bin/env python3
"""
Minimal FastAPI backend for Everbloom Archive
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List
from datetime import datetime
import sqlite3
import uuid
import os
import json
from contextlib import contextmanager

# Configuration
DATABASE_URL = "everbloom.db"
UPLOAD_DIR = "uploads"
ALLOWED_ORIGINS = ["http://localhost:8080", "http://172.24.208.1:8080"]

# Create uploads directory
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Database helper
@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def dict_from_row(row):
    return dict(row)

# FastAPI app
app = FastAPI(
    title="Everbloom Archive API",
    description="A digital archive for celebrating life and memories",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded files
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Life Events endpoints
@app.get("/life-events")
def read_life_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    featured: bool = Query(None),
    year: int = Query(None)
):
    with get_db() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM life_events"
        params = []
        
        if featured is not None:
            query += " WHERE is_featured = ?"
            params.append(1 if featured else 0)
        elif year is not None:
            query += " WHERE event_year = ?"
            params.append(year)
        
        query += " ORDER BY event_year ASC LIMIT ? OFFSET ?"
        params.extend([limit, skip])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        events = []
        for row in rows:
            event = dict_from_row(row)
            # Convert coordinates
            if event['latitude'] and event['longitude']:
                event['coordinates'] = [event['latitude'], event['longitude']]
            events.append(event)
        
        return events

@app.get("/life-events/{event_id}")
def read_life_event(event_id: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM life_events WHERE id = ?", (event_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Life event not found")
        
        event = dict_from_row(row)
        if event['latitude'] and event['longitude']:
            event['coordinates'] = [event['latitude'], event['longitude']]
        
        return event

@app.post("/life-events")
def create_life_event(event_data: dict):
    with get_db() as conn:
        cursor = conn.cursor()
        event_id = str(uuid.uuid4())
        now = datetime.now()
        
        lat, lon = None, None
        if 'coordinates' in event_data and event_data['coordinates']:
            lat, lon = event_data['coordinates']
        
        cursor.execute('''
            INSERT INTO life_events (id, event_year, title, description, location_name, latitude, longitude, is_featured, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            event_id, 
            event_data.get('event_year'), 
            event_data.get('title'), 
            event_data.get('description'), 
            event_data.get('location_name'), 
            lat, 
            lon, 
            event_data.get('is_featured', False), 
            now
        ))
        
        conn.commit()
        
        # Return created event
        return read_life_event(event_id)

# Gallery endpoints
@app.get("/gallery")
def read_gallery_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    featured: bool = Query(None),
    event_id: str = Query(None)
):
    with get_db() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM gallery"
        params = []
        
        if featured is not None:
            query += " WHERE is_featured = ?"
            params.append(1 if featured else 0)
        elif event_id is not None:
            query += " WHERE event_id = ?"
            params.append(event_id)
        
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, skip])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        return [dict_from_row(row) for row in rows]

@app.post("/gallery")
async def create_gallery_item(
    title: str = None,
    caption: str = None,
    description: str = None,
    is_featured: bool = False,
    media_type: str = "image",
    event_id: str = None,
    file: UploadFile = File(...)
):
    # Save file
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Create gallery item
    with get_db() as conn:
        cursor = conn.cursor()
        item_id = str(uuid.uuid4())
        now = datetime.now()
        
        cursor.execute('''
            INSERT INTO gallery (id, event_id, media_url, caption, is_featured, media_type, title, description, file_size, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (item_id, event_id, f"/uploads/{unique_filename}", caption, is_featured, media_type, title, description, len(content), now))
        
        conn.commit()
        
        # Return created item
        cursor.execute("SELECT * FROM gallery WHERE id = ?", (item_id,))
        row = cursor.fetchone()
        return dict_from_row(row)

@app.get("/gallery/{item_id}")
def get_gallery_item(item_id: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM gallery WHERE id = ?", (item_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Gallery item not found")
        
        return dict_from_row(row)

# Tributes endpoints
@app.get("/tributes")
def read_tributes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    approved_only: bool = Query(True),
    candles_only: bool = Query(None)
):
    with get_db() as conn:
        cursor = conn.cursor()
        query = "SELECT id, author_name, relation_to_deceased, message, candle_lit, created_at FROM tributes"
        params = []
        
        conditions = []
        if approved_only:
            conditions.append("approved = 1")
        if candles_only:
            conditions.append("candle_lit = 1")
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, skip])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        return [dict_from_row(row) for row in rows]

@app.post("/tributes")
def create_tribute(tribute_data: dict):
    with get_db() as conn:
        cursor = conn.cursor()
        tribute_id = str(uuid.uuid4())
        now = datetime.now()
        
        cursor.execute('''
            INSERT INTO tributes (id, author_name, relation_to_deceased, message, candle_lit, email, approved, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            tribute_id, 
            tribute_data.get('author_name'), 
            tribute_data.get('relation_to_deceased'), 
            tribute_data.get('message'), 
            tribute_data.get('candle_lit', False), 
            tribute_data.get('email'), 
            False,  # Not approved by default
            now
        ))
        
        conn.commit()
        
        # Return created tribute
        cursor.execute("SELECT * FROM tributes WHERE id = ?", (tribute_id,))
        row = cursor.fetchone()
        return dict_from_row(row)

@app.post("/tributes/{tribute_id}/light-candle")
def light_candle(tribute_id: str):
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Check if tribute exists
        cursor.execute("SELECT * FROM tributes WHERE id = ?", (tribute_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Tribute not found")
        
        # Update candle status
        cursor.execute("UPDATE tributes SET candle_lit = 1 WHERE id = ?", (tribute_id,))
        conn.commit()
        
        cursor.execute("SELECT * FROM tributes WHERE id = ?", (tribute_id,))
        row = cursor.fetchone()
        return dict_from_row(row)

# Root endpoint
@app.get("/")
def read_root():
    return {
        "message": "Everbloom Archive API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "life_events": "/life-events",
            "gallery": "/gallery",
            "tributes": "/tributes"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
