#!/usr/bin/env python3
"""
Flask backend with WebSocket support for Everbloom Archive
"""
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
import sqlite3
import uuid
import os
from datetime import datetime
from contextlib import contextmanager
from werkzeug.utils import secure_filename

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

# Flask app
app = Flask(__name__)
CORS(app, origins=ALLOWED_ORIGINS)

# Configure upload
app.config['UPLOAD_FOLDER'] = UPLOAD_DIR
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# SocketIO setup
socketio = SocketIO(app, cors_allowed_origins=ALLOWED_ORIGINS)

# WebSocket events
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('connected', {'message': 'Connected to Everbloom Archive'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('join_tributes')
def handle_join_tributes():
    """Join the tributes room for real-time updates"""
    join_room('tributes')
    emit('joined_tributes', {'message': 'Joined tributes room'})

@socketio.on('leave_tributes')
def handle_leave_tributes():
    """Leave the tributes room"""
    leave_room('tributes')
    emit('left_tributes', {'message': 'Left tributes room'})

# Helper function to broadcast candle updates
def broadcast_candle_update(tribute_id, candle_lit):
    """Broadcast candle lighting updates to all clients in tributes room"""
    socketio.emit('candle_update', {
        'tribute_id': tribute_id,
        'candle_lit': candle_lit,
        'timestamp': datetime.now().isoformat()
    }, room='tributes')

def broadcast_new_tribute(tribute):
    """Broadcast new tribute to all clients in tributes room"""
    socketio.emit('new_tribute', {
        'id': tribute['id'],
        'author_name': tribute['author_name'],
        'relation_to_deceased': tribute['relation_to_deceased'],
        'message': tribute['message'],
        'candle_lit': tribute['candle_lit'],
        'created_at': tribute['created_at']
    }, room='tributes')

# Life Events endpoints
@app.route("/life-events", methods=["GET"])
def read_life_events():
    skip = int(request.args.get("skip", 0))
    limit = int(request.args.get("limit", 100))
    featured = request.args.get("featured")
    year = request.args.get("year")
    
    with get_db() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM life_events"
        params = []
        
        if featured is not None:
            query += " WHERE is_featured = ?"
            params.append(1 if featured == "true" else 0)
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
        
        return jsonify(events)

@app.route("/life-events/<event_id>", methods=["GET"])
def read_life_event(event_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM life_events WHERE id = ?", (event_id,))
        row = cursor.fetchone()
        
        if not row:
            return jsonify({"error": "Life event not found"}), 404
        
        event = dict_from_row(row)
        if event['latitude'] and event['longitude']:
            event['coordinates'] = [event['latitude'], event['longitude']]
        
        return jsonify(event)

@app.route("/life-events", methods=["POST"])
def create_life_event():
    event_data = request.get_json()
    
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
        return jsonify({"id": event_id, "message": "Life event created successfully"}), 201

# Gallery endpoints
@app.route("/gallery", methods=["GET"])
def read_gallery_items():
    skip = int(request.args.get("skip", 0))
    limit = int(request.args.get("limit", 100))
    featured = request.args.get("featured")
    event_id = request.args.get("event_id")
    
    with get_db() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM gallery"
        params = []
        
        if featured is not None:
            query += " WHERE is_featured = ?"
            params.append(1 if featured == "true" else 0)
        elif event_id is not None:
            query += " WHERE event_id = ?"
            params.append(event_id)
        
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, skip])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        return jsonify([dict_from_row(row) for row in rows])

@app.route("/gallery", methods=["POST"])
def create_gallery_item():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    # Get form data
    title = request.form.get('title')
    caption = request.form.get('caption')
    description = request.form.get('description')
    is_featured = request.form.get('is_featured', 'false') == 'true'
    media_type = request.form.get('media_type', 'image')
    event_id = request.form.get('event_id')
    
    # Save file
    filename = secure_filename(file.filename)
    file_extension = os.path.splitext(filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    
    file.save(file_path)
    
    # Create gallery item
    with get_db() as conn:
        cursor = conn.cursor()
        item_id = str(uuid.uuid4())
        now = datetime.now()
        
        cursor.execute('''
            INSERT INTO gallery (id, event_id, media_url, caption, is_featured, media_type, title, description, file_size, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (item_id, event_id, f"/uploads/{unique_filename}", caption, is_featured, media_type, title, description, os.path.getsize(file_path), now))
        
        conn.commit()
        
        # Return created item
        cursor.execute("SELECT * FROM gallery WHERE id = ?", (item_id,))
        row = cursor.fetchone()
        return jsonify(dict_from_row(row)), 201

@app.route("/gallery/<item_id>", methods=["GET"])
def get_gallery_item(item_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM gallery WHERE id = ?", (item_id,))
        row = cursor.fetchone()
        
        if not row:
            return jsonify({"error": "Gallery item not found"}), 404
        
        return jsonify(dict_from_row(row))

# Tributes endpoints
@app.route("/tributes", methods=["GET"])
def read_tributes():
    skip = int(request.args.get("skip", 0))
    limit = int(request.args.get("limit", 100))
    approved_only = request.args.get("approved_only", "true") == "true"
    candles_only = request.args.get("candles_only")
    
    with get_db() as conn:
        cursor = conn.cursor()
        query = "SELECT id, author_name, relation_to_deceased, message, candle_lit, created_at FROM tributes"
        params = []
        
        conditions = []
        if approved_only:
            conditions.append("approved = 1")
        if candles_only == "true":
            conditions.append("candle_lit = 1")
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, skip])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        return jsonify([dict_from_row(row) for row in rows])

@app.route("/tributes", methods=["POST"])
def create_tribute():
    tribute_data = request.get_json()
    
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
        
        # Get the created tribute
        cursor.execute("SELECT * FROM tributes WHERE id = ?", (tribute_id,))
        tribute = dict_from_row(cursor.fetchone())
        
        # Broadcast new tribute if approved
        if tribute.get('approved'):
            broadcast_new_tribute(tribute)
        
        return jsonify(tribute), 201

@app.route("/tributes/<tribute_id>/light-candle", methods=["POST"])
def light_candle(tribute_id):
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Check if tribute exists
        cursor.execute("SELECT * FROM tributes WHERE id = ?", (tribute_id,))
        row = cursor.fetchone()
        
        if not row:
            return jsonify({"error": "Tribute not found"}), 404
        
        # Update candle status
        cursor.execute("UPDATE tributes SET candle_lit = 1 WHERE id = ?", (tribute_id,))
        conn.commit()
        
        cursor.execute("SELECT * FROM tributes WHERE id = ?", (tribute_id,))
        tribute = dict_from_row(cursor.fetchone())
        
        # Broadcast candle update
        broadcast_candle_update(tribute_id, True)
        
        return jsonify(tribute)

# Root endpoint
@app.route("/")
def read_root():
    return jsonify({
        "message": "Everbloom Archive API with WebSocket support",
        "version": "1.0.0",
        "features": ["WebSocket", "Real-time updates", "File upload"],
        "endpoints": {
            "life_events": "/life-events",
            "gallery": "/gallery",
            "tributes": "/tributes"
        },
        "websocket_events": ["candle_update", "new_tribute"]
    })

@app.route("/health")
def health_check():
    return jsonify({"status": "healthy", "websocket": "enabled"})

# Serve uploaded files
@app.route("/uploads/<filename>")
def serve_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=8000, debug=True)
