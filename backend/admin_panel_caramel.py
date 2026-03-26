#!/usr/bin/env python3
"""
Improved Admin Panel with Calm Caramel Color Scheme
"""
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import uuid
import os
from datetime import datetime
from contextlib import contextmanager

# Configuration
DATABASE_URL = "everbloom.db"
ALLOWED_ORIGINS = ["http://localhost:8080", "http://172.24.208.1:8080"]

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

# Initialize database with admin user
def init_admin_db():
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
            admin_password_hash = generate_password_hash("admin123")
            cursor.execute('''
                INSERT INTO users (id, username, email, password_hash, role)
                VALUES (?, ?, ?, ?, ?)
            ''', (admin_id, "admin", "admin@everbloom.archive", admin_password_hash, "admin"))
            conn.commit()
            print("Admin user created: username='admin', password='admin123'")

# Flask app
app = Flask(__name__)
CORS(app, origins=ALLOWED_ORIGINS)

# Initialize database
init_admin_db()

# Session storage (simple in-memory for demo)
sessions = {}

# Authentication endpoint
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
        
        # Create session
        session_id = str(uuid.uuid4())
        sessions[session_id] = {
            'user_id': user['id'],
            'username': user['username'],
            'role': user['role'],
            'login_time': datetime.now()
        }
        
        return jsonify({
            "session_id": session_id,
            "user": {
                "id": user['id'],
                "username": user['username'],
                "email": user['email'],
                "role": user['role']
            }
        })

# Session validation
@app.route("/auth/validate", methods=["POST"])
def validate_session():
    data = request.get_json()
    session_id = data.get("session_id")
    
    if not session_id or session_id not in sessions:
        return jsonify({"error": "Invalid session"}), 401
    
    return jsonify({"valid": True, "user": sessions[session_id]})

# Logout
@app.route("/auth/logout", methods=["POST"])
def logout():
    data = request.get_json()
    session_id = data.get("session_id")
    
    if session_id in sessions:
        del sessions[session_id]
    
    return jsonify({"message": "Logged out successfully"})

# Get tributes
@app.route("/tributes", methods=["GET"])
def get_tributes():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tributes ORDER BY created_at DESC")
        tributes = cursor.fetchall()
        
        return jsonify([dict_from_row(tribute) for tribute in tributes])

# Get users
@app.route("/admin/users", methods=["GET"])
def get_users():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, role, is_active, created_at, last_login FROM users")
        users = cursor.fetchall()
        
        return jsonify([dict_from_row(user) for user in users])

# Admin Panel HTML with Calm Caramel Theme
ADMIN_PANEL_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Everbloom Archive - Admin Panel</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #f4e4c1 0%, #d4a574 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .login-container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 3rem;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(139, 69, 19, 0.15);
            width: 100%;
            max-width: 400px;
            text-align: center;
            border: 1px solid rgba(212, 165, 116, 0.3);
        }

        .logo {
            width: 80px;
            height: 80px;
            background: linear-gradient(135deg, #d4a574 0%, #b08968 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 2rem;
            font-size: 2rem;
            box-shadow: 0 10px 20px rgba(212, 165, 116, 0.3);
        }

        .logo::before {
            content: "🌸";
        }

        h1 {
            color: #5d4037;
            margin-bottom: 0.5rem;
            font-size: 1.8rem;
            font-weight: 600;
        }

        .subtitle {
            color: #8d6e63;
            margin-bottom: 2rem;
            font-size: 0.9rem;
        }

        .form-group {
            margin-bottom: 1.5rem;
            text-align: left;
        }

        label {
            display: block;
            margin-bottom: 0.5rem;
            color: #5d4037;
            font-weight: 500;
        }

        input {
            width: 100%;
            padding: 0.75rem 1rem;
            border: 2px solid #d4a574;
            border-radius: 12px;
            font-size: 1rem;
            transition: all 0.3s ease;
            background: rgba(255, 255, 255, 0.8);
        }

        input:focus {
            outline: none;
            border-color: #b08968;
            box-shadow: 0 0 0 3px rgba(212, 165, 116, 0.2);
        }

        .btn {
            width: 100%;
            padding: 0.75rem 1.5rem;
            background: linear-gradient(135deg, #d4a574 0%, #b08968 100%);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 1rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(212, 165, 116, 0.3);
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(212, 165, 116, 0.4);
        }

        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        .error {
            background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
            color: #c62828;
            padding: 0.75rem;
            border-radius: 12px;
            margin-top: 1rem;
            font-size: 0.9rem;
            border: 1px solid rgba(244, 67, 54, 0.2);
        }

        .admin-container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(139, 69, 19, 0.15);
            width: 100%;
            max-width: 1200px;
            padding: 2rem;
            border: 1px solid rgba(212, 165, 116, 0.3);
        }

        .admin-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 2px solid rgba(212, 165, 116, 0.2);
        }

        .admin-title {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .admin-title h1 {
            color: #5d4037;
            font-size: 1.8rem;
        }

        .user-info {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .user-avatar {
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, #d4a574 0%, #b08968 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            box-shadow: 0 4px 10px rgba(212, 165, 116, 0.3);
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }

        .stat-card {
            background: linear-gradient(135deg, #fff8e1 0%, #ffecb3 100%);
            padding: 1.5rem;
            border-radius: 16px;
            text-align: center;
            border: 1px solid rgba(212, 165, 116, 0.3);
            box-shadow: 0 8px 20px rgba(212, 165, 116, 0.15);
        }

        .stat-value {
            font-size: 2.5rem;
            font-weight: bold;
            color: #5d4037;
            margin-bottom: 0.5rem;
        }

        .stat-label {
            color: #8d6e63;
            font-size: 0.9rem;
            font-weight: 500;
        }

        .section {
            margin-bottom: 2rem;
        }

        .section-title {
            font-size: 1.5rem;
            color: #5d4037;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .tribute-list {
            display: grid;
            gap: 1rem;
        }

        .tribute-card {
            background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
            padding: 1.5rem;
            border-radius: 16px;
            border-left: 4px solid #d4a574;
            border: 1px solid rgba(212, 165, 116, 0.2);
            box-shadow: 0 4px 15px rgba(212, 165, 116, 0.1);
        }

        .tribute-header {
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 1rem;
        }

        .tribute-author {
            font-weight: 600;
            color: #5d4037;
        }

        .tribute-date {
            color: #8d6e63;
            font-size: 0.9rem;
        }

        .tribute-message {
            color: #6d4c41;
            line-height: 1.6;
            margin-bottom: 1rem;
        }

        .candle-status {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.25rem 0.75rem;
            background: linear-gradient(135deg, #fff8e1 0%, #ffecb3 100%);
            color: #8d6e63;
            border-radius: 20px;
            font-size: 0.8rem;
            border: 1px solid rgba(212, 165, 116, 0.3);
        }

        .candle-status.lit {
            background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
            color: #4caf50;
            border-color: rgba(76, 175, 80, 0.3);
        }

        .hidden {
            display: none;
        }

        .loading {
            text-align: center;
            padding: 2rem;
            color: #8d6e63;
        }

        @media (max-width: 768px) {
            .login-container,
            .admin-container {
                margin: 1rem;
                padding: 2rem;
            }

            .admin-header {
                flex-direction: column;
                gap: 1rem;
                text-align: center;
            }

            .stats-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <!-- Login Form -->
    <div id="loginForm" class="login-container">
        <div class="logo"></div>
        <h1>Admin Panel</h1>
        <p class="subtitle">Everbloom Archive Management</p>
        
        <form id="loginFormElement">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" value="admin" required>
            </div>
            
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" value="admin123" required>
            </div>
            
            <button type="submit" class="btn" id="loginBtn">
                Sign In
            </button>
        </form>
        
        <div id="errorMessage" class="error hidden"></div>
    </div>

    <!-- Admin Panel -->
    <div id="adminPanel" class="admin-container hidden">
        <div class="admin-header">
            <div class="admin-title">
                <div class="logo" style="width: 40px; height: 40px; font-size: 1rem;"></div>
                <h1>Everbloom Archive</h1>
            </div>
            
            <div class="user-info">
                <span id="userDisplay">Admin</span>
                <div class="user-avatar">A</div>
                <button class="btn" onclick="logout()" style="width: auto; padding: 0.5rem 1rem;">
                    Logout
                </button>
            </div>
        </div>

        <!-- Statistics -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value" id="totalTributes">0</div>
                <div class="stat-label">Total Tributes</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-value" id="candlesLit">0</div>
                <div class="stat-label">Candles Lit</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-value" id="totalUsers">0</div>
                <div class="stat-label">Users</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-value" id="todayTributes">0</div>
                <div class="stat-label">Today's Tributes</div>
            </div>
        </div>

        <!-- Recent Tributes -->
        <div class="section">
            <h2 class="section-title">
                🕯️ Recent Tributes
            </h2>
            
            <div id="tributesList" class="tribute-list">
                <div class="loading">Loading tributes...</div>
            </div>
        </div>
    </div>

    <script>
        let sessionId = localStorage.getItem('adminSession');

        // Check if already logged in
        if (sessionId) {
            validateSession();
        }

        // Login form submission
        document.getElementById('loginFormElement').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const loginBtn = document.getElementById('loginBtn');
            const errorMsg = document.getElementById('errorMessage');
            
            loginBtn.disabled = true;
            loginBtn.textContent = 'Signing in...';
            errorMsg.classList.add('hidden');
            
            try {
                const response = await fetch('/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    sessionId = data.session_id;
                    localStorage.setItem('adminSession', sessionId);
                    showAdminPanel();
                } else {
                    errorMsg.textContent = data.error || 'Login failed';
                    errorMsg.classList.remove('hidden');
                }
            } catch (error) {
                errorMsg.textContent = 'Network error. Please try again.';
                errorMsg.classList.remove('hidden');
            } finally {
                loginBtn.disabled = false;
                loginBtn.textContent = 'Sign In';
            }
        });

        async function validateSession() {
            try {
                const response = await fetch('/auth/validate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ session_id: sessionId })
                });
                
                if (response.ok) {
                    showAdminPanel();
                } else {
                    localStorage.removeItem('adminSession');
                    sessionId = null;
                }
            } catch (error) {
                localStorage.removeItem('adminSession');
                sessionId = null;
            }
        }

        function showAdminPanel() {
            document.getElementById('loginForm').classList.add('hidden');
            document.getElementById('adminPanel').classList.remove('hidden');
            loadDashboard();
        }

        function showLoginForm() {
            document.getElementById('loginForm').classList.remove('hidden');
            document.getElementById('adminPanel').classList.add('hidden');
        }

        async function logout() {
            if (sessionId) {
                try {
                    await fetch('/auth/logout', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ session_id: sessionId })
                    });
                } catch (error) {
                    console.error('Logout error:', error);
                }
            }
            
            localStorage.removeItem('adminSession');
            sessionId = null;
            showLoginForm();
        }

        async function loadDashboard() {
            await Promise.all([
                loadStats(),
                loadTributes()
            ]);
        }

        async function loadStats() {
            try {
                const [tributesResponse, usersResponse] = await Promise.all([
                    fetch('/tributes'),
                    fetch('/admin/users')
                ]);

                if (tributesResponse.ok && usersResponse.ok) {
                    const tributes = await tributesResponse.json();
                    const users = await usersResponse.json();
                    
                    const candleCount = tributes.filter(t => t.candle_lit).length;
                    const today = new Date().toDateString();
                    const todayTributes = tributes.filter(t => 
                        new Date(t.created_at).toDateString() === today
                    ).length;
                    
                    document.getElementById('totalTributes').textContent = tributes.length;
                    document.getElementById('candlesLit').textContent = candleCount;
                    document.getElementById('totalUsers').textContent = users.length;
                    document.getElementById('todayTributes').textContent = todayTributes;
                }
            } catch (error) {
                console.error('Failed to load stats:', error);
            }
        }

        async function loadTributes() {
            try {
                const response = await fetch('/tributes');
                
                if (response.ok) {
                    const tributes = await response.json();
                    const tributesList = document.getElementById('tributesList');
                    
                    if (tributes.length === 0) {
                        tributesList.innerHTML = '<div class="loading">No tributes yet</div>';
                        return;
                    }
                    
                    tributesList.innerHTML = tributes.slice(0, 10).map(tribute => `
                        <div class="tribute-card">
                            <div class="tribute-header">
                                <div>
                                    <div class="tribute-author">${tribute.author_name}</div>
                                    ${tribute.relation_to_deceased ? `<div style="color: #8d6e63; font-size: 0.9rem;">${tribute.relation_to_deceased}</div>` : ''}
                                </div>
                                <div class="tribute-date">${new Date(tribute.created_at).toLocaleDateString()}</div>
                            </div>
                            
                            <div class="tribute-message">${tribute.message}</div>
                            
                            <div class="candle-status ${tribute.candle_lit ? 'lit' : ''}">
                                ${tribute.candle_lit ? '🕯️ Candle lit' : '🕯️ No candle'}
                            </div>
                        </div>
                    `).join('');
                }
            } catch (error) {
                console.error('Failed to load tributes:', error);
                document.getElementById('tributesList').innerHTML = '<div class="loading">Failed to load tributes</div>';
            }
        }
    </script>
</body>
</html>
"""

@app.route("/admin")
def admin_panel():
    return render_template_string(ADMIN_PANEL_HTML)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8002, debug=True)
