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

@app.route("/auth/refresh", methods=["POST"])
@jwt_refresh_token_required
def refresh():
    current_user_id = get_jwt_identity()
    new_token = create_access_token(identity=current_user_id)
    return jsonify({"access_token": new_token})

@app.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    
    if not all([username, email, password]):
        return jsonify({"error": "Username, email, and password required"}), 400
    
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, email))
        if cursor.fetchone():
            return jsonify({"error": "Username or email already exists"}), 409
        
        # Create user
        user_id = str(uuid.uuid4())
        password_hash = generate_password_hash(password)
        
        cursor.execute('''
            INSERT INTO users (id, username, email, password_hash)
            VALUES (?, ?, ?, ?)
        ''', (user_id, username, email, password_hash))
        conn.commit()
        
        return jsonify({
            "message": "User created successfully",
            "user": {
                "id": user_id,
                "username": username,
                "email": email,
                "role": "user"
            }
        }), 201

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

@app.route("/admin/users/<user_id>/toggle", methods=["POST"])
@jwt_required()
def toggle_user_status(user_id):
    current_user_id = get_jwt_identity()
    
    # Check if user is admin
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE id = ?", (current_user_id,))
        user = cursor.fetchone()
        
        if not user or user['role'] != 'admin':
            return jsonify({"error": "Admin access required"}), 403
        
        # Toggle user status
        cursor.execute("UPDATE users SET is_active = NOT is_active WHERE id = ?", (user_id,))
        conn.commit()
        
        cursor.execute("SELECT is_active FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        
        return jsonify({
            "user_id": user_id,
            "is_active": bool(result['is_active']) if result else False
        })

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

# Admin panel HTML
ADMIN_PANEL_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Everbloom Archive - Admin Panel</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f8fafc; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .card { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .btn { padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; }
        .btn-primary { background: #3b82f6; color: white; }
        .btn-success { background: #10b981; color: white; }
        .btn-danger { background: #ef4444; color: white; }
        .btn:hover { opacity: 0.9; }
        .table { width: 100%; border-collapse: collapse; }
        .table th, .table td { padding: 12px; text-align: left; border-bottom: 1px solid #e5e7eb; }
        .badge { padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: bold; }
        .badge-admin { background: #fef3c7; color: #92400e; }
        .badge-user { background: #dbeafe; color: #1e40af; }
        .status-active { color: #10b981; }
        .status-inactive { color: #ef4444; }
        .login-form { max-width: 400px; margin: 100px auto; padding: 30px; background: white; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: 500; }
        .form-group input { width: 100%; padding: 10px; border: 1px solid #d1d5db; border-radius: 4px; font-size: 14px; }
        .hidden { display: none; }
        .loading { text-align: center; padding: 20px; }
    </style>
</head>
<body>
    <div id="login-form" class="login-form">
        <h2 style="margin-bottom: 20px;">Admin Login</h2>
        <form id="login">
            <div class="form-group">
                <label>Username</label>
                <input type="text" id="username" required>
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" id="password" required>
            </div>
            <button type="submit" class="btn btn-primary" style="width: 100%;">Login</button>
        </form>
        <div id="login-error" style="color: #ef4444; margin-top: 10px; display: none;"></div>
    </div>

    <div id="admin-panel" class="container hidden">
        <div class="header">
            <h1>Everbloom Archive Admin Panel</h1>
            <div style="margin-top: 10px;">
                <span id="user-info"></span>
                <button id="logout" class="btn btn-danger" style="float: right;">Logout</button>
            </div>
        </div>

        <div class="card">
            <h2>Users Management</h2>
            <div id="users-loading" class="loading">Loading users...</div>
            <table id="users-table" class="table hidden">
                <thead>
                    <tr>
                        <th>Username</th>
                        <th>Email</th>
                        <th>Role</th>
                        <th>Status</th>
                        <th>Created</th>
                        <th>Last Login</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody id="users-tbody"></tbody>
            </table>
        </div>

        <div class="card">
            <h2>Pending Tributes</h2>
            <div id="tributes-loading" class="loading">Loading tributes...</div>
            <div id="tributes-container"></div>
        </div>
    </div>

    <script>
        let accessToken = localStorage.getItem('accessToken');
        
        // Check authentication on load
        if (accessToken) {
            showAdminPanel();
        }
        
        // Login form
        document.getElementById('login').addEventListener('submit', async (e) => {
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
                    accessToken = data.access_token;
                    localStorage.setItem('accessToken', accessToken);
                    showAdminPanel();
                } else {
                    document.getElementById('login-error').textContent = data.error;
                    document.getElementById('login-error').style.display = 'block';
                }
            } catch (error) {
                document.getElementById('login-error').textContent = 'Login failed';
                document.getElementById('login-error').style.display = 'block';
            }
        });
        
        // Logout
        document.getElementById('logout').addEventListener('click', () => {
            localStorage.removeItem('accessToken');
            accessToken = null;
            showLoginForm();
        });
        
        function showLoginForm() {
            document.getElementById('login-form').classList.remove('hidden');
            document.getElementById('admin-panel').classList.add('hidden');
        }
        
        function showAdminPanel() {
            document.getElementById('login-form').classList.add('hidden');
            document.getElementById('admin-panel').classList.remove('hidden');
            loadUserInfo();
            loadUsers();
            loadPendingTributes();
        }
        
        async function loadUserInfo() {
            try {
                const response = await fetch('/api/auth/me', {
                    headers: { 'Authorization': `Bearer ${accessToken}` }
                });
                
                if (response.ok) {
                    const user = await response.json();
                    document.getElementById('user-info').textContent = `Logged in as: ${user.username} (${user.role})`;
                }
            } catch (error) {
                console.error('Failed to load user info:', error);
            }
        }
        
        async function loadUsers() {
            try {
                const response = await fetch('/api/admin/users', {
                    headers: { 'Authorization': `Bearer ${accessToken}` }
                });
                
                if (response.ok) {
                    const users = await response.json();
                    renderUsers(users);
                }
            } catch (error) {
                console.error('Failed to load users:', error);
            }
        }
        
        function renderUsers(users) {
            document.getElementById('users-loading').classList.add('hidden');
            document.getElementById('users-table').classList.remove('hidden');
            
            const tbody = document.getElementById('users-tbody');
            tbody.innerHTML = '';
            
            users.forEach(user => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${user.username}</td>
                    <td>${user.email}</td>
                    <td><span class="badge badge-${user.role}">${user.role}</span></td>
                    <td><span class="status-${user.is_active ? 'active' : 'inactive'}">${user.is_active ? 'Active' : 'Inactive'}</span></td>
                    <td>${new Date(user.created_at).toLocaleDateString()}</td>
                    <td>${user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never'}</td>
                    <td>
                        <button class="btn ${user.is_active ? 'btn-danger' : 'btn-success'}" 
                                onclick="toggleUser('${user.id}')">
                            ${user.is_active ? 'Deactivate' : 'Activate'}
                        </button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }
        
        async function toggleUser(userId) {
            try {
                const response = await fetch(`/api/admin/users/${userId}/toggle`, {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${accessToken}` }
                });
                
                if (response.ok) {
                    loadUsers();
                }
            } catch (error) {
                console.error('Failed to toggle user:', error);
            }
        }
        
        async function loadPendingTributes() {
            try {
                const response = await fetch('/api/admin/tributes/pending', {
                    headers: { 'Authorization': `Bearer ${accessToken}` }
                });
                
                if (response.ok) {
                    const tributes = await response.json();
                    renderTributes(tributes);
                }
            } catch (error) {
                console.error('Failed to load tributes:', error);
            }
        }
        
        function renderTributes(tributes) {
            document.getElementById('tributes-loading').classList.add('hidden');
            const container = document.getElementById('tributes-container');
            
            if (tributes.length === 0) {
                container.innerHTML = '<p>No pending tributes.</p>';
                return;
            }
            
            container.innerHTML = tributes.map(tribute => `
                <div class="card" style="margin-bottom: 15px;">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div>
                            <strong>${tribute.author_name}</strong>
                            ${tribute.relation_to_deceased ? ` (${tribute.relation_to_deceased})` : ''}
                            <p style="margin: 10px 0; color: #6b7280;">${tribute.message}</p>
                            <small style="color: #9ca3af;">${new Date(tribute.created_at).toLocaleString()}</small>
                        </div>
                        <button class="btn btn-success" onclick="approveTribute('${tribute.id}')">
                            Approve
                        </button>
                    </div>
                </div>
            `).join('');
        }
        
        async function approveTribute(tributeId) {
            try {
                const response = await fetch(`/api/admin/tributes/${tributeId}/approve`, {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${accessToken}` }
                });
                
                if (response.ok) {
                    loadPendingTributes();
                }
            } catch (error) {
                console.error('Failed to approve tribute:', error);
            }
        }
    </script>
</body>
</html>
"""

@app.route("/admin")
def admin_panel():
    return render_template_string(ADMIN_PANEL_HTML)

# Include all previous endpoints (life events, gallery, tributes)
# ... (previous endpoints would be included here)

# Root endpoint
@app.route("/")
def read_root():
    return jsonify({
        "message": "Everbloom Archive API with Authentication",
        "version": "2.0.0",
        "features": ["Authentication", "Admin Panel", "WebSocket", "Real-time updates", "File upload"],
        "endpoints": {
            "auth": "/auth",
            "admin": "/admin",
            "life_events": "/life-events",
            "gallery": "/gallery",
            "tributes": "/tributes"
        }
    })

@app.route("/health")
def health_check():
    return jsonify({"status": "healthy", "auth": "enabled", "websocket": "enabled"})

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=8000, debug=True)
