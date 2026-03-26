#!/usr/bin/env python3
"""
Simple database creation script for SQLite
"""
import sqlite3
import os
from datetime import datetime

def create_database():
    """Create SQLite database with required tables"""
    
    # Remove existing database if it exists
    if os.path.exists('everbloom.db'):
        os.remove('everbloom.db')
    
    # Create connection
    conn = sqlite3.connect('everbloom.db')
    cursor = conn.cursor()
    
    # Create life_events table
    cursor.execute('''
        CREATE TABLE life_events (
            id TEXT PRIMARY KEY,
            event_year INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            location_name TEXT,
            latitude REAL,
            longitude REAL,
            is_featured BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP
        )
    ''')
    
    # Create gallery table
    cursor.execute('''
        CREATE TABLE gallery (
            id TEXT PRIMARY KEY,
            event_id TEXT,
            media_url TEXT NOT NULL,
            caption TEXT,
            is_featured BOOLEAN DEFAULT 0,
            media_type TEXT DEFAULT 'image',
            title TEXT,
            description TEXT,
            file_size INTEGER,
            width INTEGER,
            height INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (event_id) REFERENCES life_events (id)
        )
    ''')
    
    # Create tributes table
    cursor.execute('''
        CREATE TABLE tributes (
            id TEXT PRIMARY KEY,
            author_name TEXT NOT NULL,
            relation_to_deceased TEXT,
            message TEXT NOT NULL,
            candle_lit BOOLEAN DEFAULT 0,
            approved BOOLEAN DEFAULT 0,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create indexes
    cursor.execute('CREATE INDEX idx_life_events_year ON life_events(event_year)')
    cursor.execute('CREATE INDEX idx_life_events_featured ON life_events(is_featured)')
    cursor.execute('CREATE INDEX idx_gallery_event_id ON gallery(event_id)')
    cursor.execute('CREATE INDEX idx_gallery_featured ON gallery(is_featured)')
    cursor.execute('CREATE INDEX idx_tributes_approved ON tributes(approved)')
    cursor.execute('CREATE INDEX idx_tributes_candle ON tributes(candle_lit)')
    
    # Insert sample data
    import uuid
    
    # Sample life events
    events = [
        {
            'id': str(uuid.uuid4()),
            'event_year': 1950,
            'title': 'Birth',
            'description': 'Born in Nairobi, Kenya',
            'location_name': 'Nairobi, Kenya',
            'latitude': -1.2921,
            'longitude': 36.8219,
            'is_featured': True
        },
        {
            'id': str(uuid.uuid4()),
            'event_year': 1975,
            'title': 'Marriage',
            'description': 'Married the love of her life',
            'location_name': 'Nairobi, Kenya',
            'latitude': -1.2921,
            'longitude': 36.8219,
            'is_featured': True
        },
        {
            'id': str(uuid.uuid4()),
            'event_year': 1980,
            'title': 'First Child',
            'description': 'Welcomed first child into the world',
            'location_name': 'Nairobi, Kenya',
            'latitude': -1.2921,
            'longitude': 36.8219,
            'is_featured': False
        }
    ]
    
    for event in events:
        cursor.execute('''
            INSERT INTO life_events (id, event_year, title, description, location_name, latitude, longitude, is_featured)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            event['id'], event['event_year'], event['title'], 
            event['description'], event['location_name'], 
            event['latitude'], event['longitude'], event['is_featured']
        ))
    
    # Sample gallery items
    gallery_items = [
        {
            'id': str(uuid.uuid4()),
            'event_id': events[0]['id'],
            'media_url': '/uploads/sample_baby_photo.jpg',
            'caption': 'Baby photo',
            'is_featured': True,
            'media_type': 'image',
            'title': 'First Photo',
            'description': 'A precious moment from birth'
        },
        {
            'id': str(uuid.uuid4()),
            'event_id': events[1]['id'],
            'media_url': '/uploads/wedding_photo.jpg',
            'caption': 'Wedding day',
            'is_featured': True,
            'media_type': 'image',
            'title': 'Wedding Photo',
            'description': 'Beautiful wedding ceremony'
        }
    ]
    
    for item in gallery_items:
        cursor.execute('''
            INSERT INTO gallery (id, event_id, media_url, caption, is_featured, media_type, title, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            item['id'], item['event_id'], item['media_url'], 
            item['caption'], item['is_featured'], 
            item['media_type'], item['title'], item['description']
        ))
    
    # Sample tributes
    tributes = [
        {
            'id': str(uuid.uuid4()),
            'author_name': 'John Doe',
            'relation_to_deceased': 'Grandson',
            'message': 'Grandma, you were the light of our lives. Your wisdom and love will forever guide us.',
            'candle_lit': True,
            'approved': True,
            'email': 'john@example.com'
        },
        {
            'id': str(uuid.uuid4()),
            'author_name': 'Jane Smith',
            'relation_to_deceased': 'Friend',
            'message': 'A remarkable woman who touched so many lives. Rest in peace.',
            'candle_lit': False,
            'approved': True,
            'email': 'jane@example.com'
        }
    ]
    
    for tribute in tributes:
        cursor.execute('''
            INSERT INTO tributes (id, author_name, relation_to_deceased, message, candle_lit, approved, email)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            tribute['id'], tribute['author_name'], tribute['relation_to_deceased'],
            tribute['message'], tribute['candle_lit'], tribute['approved'], tribute['email']
        ))
    
    # Commit and close
    conn.commit()
    conn.close()
    
    print("✅ Database created successfully!")
    print(f"📁 Database file: {os.path.abspath('everbloom.db')}")
    print("📊 Sample data inserted:")
    print(f"   - {len(events)} life events")
    print(f"   - {len(gallery_items)} gallery items")
    print(f"   - {len(tributes)} tributes")

if __name__ == "__main__":
    create_database()
