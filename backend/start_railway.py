#!/usr/bin/env python3
"""
Railway startup script for Everbloom Archive
"""
import os
import sqlite3
from complete_app import app, socketio, init_auth_db

# Initialize database
init_auth_db()

# Get port from Railway
port = int(os.environ.get("PORT", 8000))

if __name__ == "__main__":
    print(f"Starting Everbloom Archive on port {port}")
    socketio.run(app, host="0.0.0.0", port=port, debug=False)
