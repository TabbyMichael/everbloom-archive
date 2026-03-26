#!/usr/bin/env python3
"""
Flask backend with Authentication and Admin Panel for Everbloom Archive
"""
from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, 
    get_jwt_identity, create_refresh_token, jwt_refresh_token_required
)
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import uuid
import os
from datetime import datetime, timedelta
from contextlib import contextmanager
from werkzeug.utils import secure_filename

# Configuration
DATABASE_URL = "everbloom.db"
UPLOAD_DIR = "uploads"
ALLOWED_ORIGINS = ["http://localhost:8080", "http://172.24.208.1:8080"]
JWT_SECRET_KEY = "everbloom-jwt-secret-key-change-in-production"
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

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

# Initialize database with users table
def init_auth_db():
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # Create admin user if not exists
        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        if not cursor.fetchone():
            admin_id = str(uuid.uuid4())
            admin_password_hash = generate_password_hash("admin123")  # Change in production
            cursor.execute('''
                INSERT INTO users (id, username, email, password_hash, role)
                VALUES (?, ?, ?, ?, ?)
            ''', (admin_id, "admin", "admin@everbloom.archive", admin_password_hash, "admin"))
            conn.commit()
            print("Admin user created: username='admin', password='admin123'")

# Flask app
app = Flask(__name__)
CORS(app, origins=ALLOWED_ORIGINS)

# JWT Configuration
app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = JWT_ACCESS_TOKEN_EXPIRES
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = JWT_REFRESH_TOKEN_EXPIRES
jwt = JWTManager(app)

# Configure upload
app.config['UPLOAD_FOLDER'] = UPLOAD_DIR
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# SocketIO setup
socketio = SocketIO(app, cors_allowed_origins=ALLOWED_ORIGINS)

# Initialize auth database
init_auth_db()

# Authentication endpoints
@app.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND is_active = 1", (username,))
        user = cursor.fetchone()
        
        if not user or not check_password_hash(user['password_hash'], password):
            return jsonify({"error": "Invalid credentials"}), 401
        
        # Update last login
        cursor.execute("UPDATE users SET last_login = ? WHERE id = ?", 
                     (datetime.now(), user['id']))
        conn.commit()
        
        # Create tokens
        access_token = create_access_token(identity=user['id'])
        refresh_token = create_refresh_token(identity=user['id'])
        
        return jsonify({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": user['id'],
                "username": user['username'],
                "email": user['email'],
                "role": user['role']
            }
        })

@app.route("/auth/me", methods=["GET"])
@jwt_required()
def get_current_user():
    current_user_id = get_jwt_identity()
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, role, created_at, last_login FROM users WHERE id = ?", 
                     (current_user_id,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify(dict_from_row(user))

# Include all previous endpoints (life events, gallery, tributes)
# For brevity, just including the essential endpoints here

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
            if event['latitude'] and event['longitude']:
                event['coordinates'] = [event['latitude'], event['longitude']]
            events.append(event)
        
        return jsonify(events)

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
        socketio.emit('candle_update', {
            'tribute_id': tribute_id,
            'candle_lit': True,
            'timestamp': datetime.now().isoformat()
        }, room='tributes')
        
        return jsonify(tribute)

# Admin endpoints
@app.route("/admin/users", methods=["GET"])
@jwt_required()
def get_users():
    current_user_id = get_jwt_identity()
    
    # Check if user is admin
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE id = ?", (current_user_id,))
        user = cursor.fetchone()
        
        if not user or user['role'] != 'admin':
            return jsonify({"error": "Admin access required"}), 403
        
        cursor.execute("SELECT id, username, email, role, is_active, created_at, last_login FROM users")
        users = cursor.fetchall()
        
        return jsonify([dict_from_row(user) for user in users])

@app.route("/admin/tributes/pending", methods=["GET"])
@jwt_required()
def get_pending_tributes():
    current_user_id = get_jwt_identity()
    
    # Check if user is admin
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE id = ?", (current_user_id,))
        user = cursor.fetchone()
        
        if not user or user['role'] != 'admin':
            return jsonify({"error": "Admin access required"}), 403
        
        cursor.execute("SELECT * FROM tributes WHERE approved = 0 ORDER BY created_at DESC")
        tributes = cursor.fetchall()
        
        return jsonify([dict_from_row(tribute) for tribute in tributes])

@app.route("/admin/tributes/<tribute_id>/approve", methods=["POST"])
@jwt_required()
def approve_tribute(tribute_id):
    current_user_id = get_jwt_identity()
    
    # Check if user is admin
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE id = ?", (current_user_id,))
        user = cursor.fetchone()
        
        if not user or user['role'] != 'admin':
            return jsonify({"error": "Admin access required"}), 403
        
        # Approve tribute
        cursor.execute("UPDATE tributes SET approved = 1 WHERE id = ?", (tribute_id,))
        conn.commit()
        
        # Get approved tribute
        cursor.execute("SELECT * FROM tributes WHERE id = ?", (tribute_id,))
        tribute = dict_from_row(cursor.fetchone())
        
        # Broadcast new tribute
        socketio.emit('new_tribute', {
            'id': tribute['id'],
            'author_name': tribute['author_name'],
            'relation_to_deceased': tribute['relation_to_deceased'],
            'message': tribute['message'],
            'candle_lit': tribute['candle_lit'],
            'created_at': tribute['created_at']
        }, room='tributes')
        
        return jsonify({"message": "Tribute approved successfully"})

# Admin panel HTML (simplified)
ADMIN_PANEL_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Everbloom Archive - Admin Panel</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }
        .login { max-width: 400px; margin: 100px auto; }
        .btn { padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        .btn-primary { background: #007bff; color: white; }
        .btn-success { background: #28a745; color: white; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 5px; }
        .form-group input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
        .hidden { display: none; }
        .card { border: 1px solid #ddd; border-radius: 8px; padding: 20px; margin-bottom: 20px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
    </style>
</head>
<body>
    <div id="login" class="login">
        <div class="card">
            <h2>Admin Login</h2>
            <form id="loginForm">
                <div class="form-group">
                    <label>Username:</label>
                    <input type="text" id="username" required>
                </div>
                <div class="form-group">
                    <label>Password:</label>
                    <input type="password" id="password" required>
                </div>
                <button type="submit" class="btn btn-primary">Login</button>
            </form>
            <div id="error" style="color: red; margin-top: 10px;"></div>
        </div>
    </div>

    <div id="adminPanel" class="container hidden">
        <h1>Everbloom Archive Admin Panel</h1>
        <button id="logout" class="btn" style="float: right;">Logout</button>
        
        <div class="card">
            <h2>Pending Tributes</h2>
            <div id="tributes"></div>
        </div>
    </div>

    <script>
        let token = localStorage.getItem('token');

        document.getElementById('loginForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;

            try {
                const response = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });

                const data = await response.json();
                if (response.ok) {
                    token = data.access_token;
                    localStorage.setItem('token', token);
                    showPanel();
                } else {
                    document.getElementById('error').textContent = data.error;
                }
            } catch (error) {
                document.getElementById('error').textContent = 'Login failed';
            }
        });

        document.getElementById('logout').addEventListener('click', () => {
            localStorage.removeItem('token');
            token = null;
            showLogin();
        });

        function showLogin() {
            document.getElementById('login').classList.remove('hidden');
            document.getElementById('adminPanel').classList.add('hidden');
        }

        function showPanel() {
            document.getElementById('login').classList.add('hidden');
            document.getElementById('adminPanel').classList.remove('hidden');
            loadTributes();
        }

        async function loadTributes() {
            try {
                const response = await fetch('/api/admin/tributes/pending', {
                    headers: { 'Authorization': `Bearer ${token}` }
                });

                if (response.ok) {
                    const tributes = await response.json();
                    const container = document.getElementById('tributes');
                    
                    if (tributes.length === 0) {
                        container.innerHTML = '<p>No pending tributes</p>';
                    } else {
                        container.innerHTML = tributes.map(t => `
                            <div class="card">
                                <strong>${t.author_name}</strong> ${t.relation_to_deceased ? `(${t.relation_to_deceased})` : ''}
                                <p>${t.message}</p>
                                <small>${new Date(t.created_at).toLocaleString()}</small>
                                <button class="btn btn-success" onclick="approve('${t.id}')">Approve</button>
                            </div>
                        `).join('');
                    }
                }
            } catch (error) {
                console.error('Failed to load tributes:', error);
            }
        }

        async function approve(id) {
            try {
                const response = await fetch(`/api/admin/tributes/${id}/approve`, {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${token}` }
                });

                if (response.ok) {
                    loadTributes();
                }
            } catch (error) {
                console.error('Failed to approve tribute:', error);
            }
        }

        if (token) {
            showPanel();
        }
    </script>
</body>
</html>
"""

@app.route("/admin")
def admin_panel():
    return render_template_string(ADMIN_PANEL_HTML)

# Root endpoint
@app.route("/")
def read_root():
    return jsonify({
        "message": "Everbloom Archive API with Authentication",
        "version": "2.0.0",
        "features": ["Authentication", "Admin Panel", "WebSocket", "Real-time updates"],
        "endpoints": {
            "auth": "/auth",
            "admin": "/admin",
            "life_events": "/life-events",
            "tributes": "/tributes"
        }
    })

@app.route("/health")
def health_check():
    return jsonify({"status": "healthy", "auth": "enabled"})

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=8000, debug=True)
