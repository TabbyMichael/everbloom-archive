# Database Schema Documentation

## Overview

The Everbloom Archive uses PostgreSQL as its primary database with the PostGIS extension for geographical data. The schema is designed to support a rich, interactive memorial experience with proper relationships and indexing.

## Database Setup

### Create Database
```sql
CREATE DATABASE everbloom;
CREATE USER everbloom_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE everbloom TO everbloom_user;
```

### Enable Extensions
```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable PostGIS for geographical data
CREATE EXTENSION IF NOT EXISTS "postgis";
```

## Tables

### 1. life_events

Stores significant life events and milestones.

```sql
CREATE TABLE life_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_year INTEGER NOT NULL CHECK (event_year >= 1900 AND event_year <= 2100),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    location_name VARCHAR(255),
    coordinates POINT, -- PostGIS point for geographical data
    is_featured BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for performance
CREATE INDEX idx_life_events_year ON life_events(event_year);
CREATE INDEX idx_life_events_featured ON life_events(is_featured);
CREATE INDEX idx_life_events_location ON life_events USING GIST(coordinates);
CREATE INDEX idx_life_events_created ON life_events(created_at);

-- Full-text search index
CREATE INDEX idx_life_events_search ON life_events USING GIN(
    to_tsvector('english', title || ' ' || COALESCE(description, '') || ' ' || COALESCE(location_name, ''))
);
```

**Sample Data:**
```sql
INSERT INTO life_events (event_year, title, description, location_name, coordinates, is_featured) VALUES
(1950, 'Birth', 'Born in Nairobi, Kenya', 'Nairobi, Kenya', ST_MakePoint(-1.2921, 36.8219), true),
(1975, 'Marriage', 'Married the love of her life', 'Nairobi, Kenya', ST_MakePoint(-1.2921, 36.8219), false),
(1980, 'First Child', 'Welcomed first child into the world', 'Nairobi, Kenya', ST_MakePoint(-1.2921, 36.8219), true);
```

### 2. gallery

Stores photos, videos, and other media files.

```sql
CREATE TABLE gallery (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_id UUID REFERENCES life_events(id) ON DELETE SET NULL,
    media_url TEXT NOT NULL,
    caption TEXT,
    is_featured BOOLEAN DEFAULT FALSE,
    media_type VARCHAR(50) DEFAULT 'image' CHECK (media_type IN ('image', 'video')),
    title VARCHAR(255),
    description TEXT,
    file_size INTEGER, -- in bytes
    width INTEGER,
    height INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_gallery_event_id ON gallery(event_id);
CREATE INDEX idx_gallery_featured ON gallery(is_featured);
CREATE INDEX idx_gallery_type ON gallery(media_type);
CREATE INDEX idx_gallery_created ON gallery(created_at);

-- Full-text search index
CREATE INDEX idx_gallery_search ON gallery USING GIN(
    to_tsvector('english', COALESCE(title, '') || ' ' || COALESCE(caption, '') || ' ' || COALESCE(description, ''))
);
```

**Sample Data:**
```sql
INSERT INTO gallery (event_id, media_url, caption, is_featured, media_type, title, description, file_size, width, height) VALUES
((SELECT id FROM life_events WHERE title = 'Birth'), '/uploads/birth_photo.jpg', 'Baby photo', true, 'image', 'First Photo', 'A precious moment from birth', 1024000, 800, 600),
((SELECT id FROM life_events WHERE title = 'Marriage'), '/uploads/wedding_photo.jpg', 'Wedding day', true, 'image', 'Wedding Photo', 'Beautiful wedding ceremony', 2048000, 1200, 800);
```

### 3. tributes

Stores user tributes, condolences, and messages.

```sql
CREATE TABLE tributes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    author_name VARCHAR(100) NOT NULL,
    relation_to_deceased VARCHAR(100),
    message TEXT NOT NULL,
    candle_lit BOOLEAN DEFAULT FALSE,
    approved BOOLEAN DEFAULT FALSE, -- Moderation system
    email VARCHAR(255), -- For verification/contact
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_tributes_approved ON tributes(approved);
CREATE INDEX idx_tributes_candle ON tributes(candle_lit);
CREATE INDEX idx_tributes_created ON tributes(created_at);
CREATE INDEX idx_tributes_author ON tributes(author_name);

-- Full-text search index
CREATE INDEX idx_tributes_search ON tributes USING GIN(
    to_tsvector('english', author_name || ' ' || COALESCE(relation_to_deceased, '') || ' ' || message)
);
```

**Sample Data:**
```sql
INSERT INTO tributes (author_name, relation_to_deceased, message, candle_lit, approved, email) VALUES
('John Doe', 'Grandson', 'Grandma, you were the light of our lives. Your wisdom and love will forever guide us.', true, true, 'john@example.com'),
('Jane Smith', 'Friend', 'A remarkable woman who touched so many lives. Rest in peace.', false, true, 'jane@example.com'),
('Bob Johnson', 'Nephew', 'Your stories and laughter will be missed dearly.', true, false, 'bob@example.com'); -- Pending approval
```

## Views

### Public Gallery View
```sql
CREATE VIEW public_gallery AS
SELECT 
    g.id,
    g.media_url,
    g.caption,
    g.title,
    g.description,
    g.media_type,
    g.file_size,
    g.width,
    g.height,
    g.created_at,
    le.title as event_title,
    le.event_year
FROM gallery g
LEFT JOIN life_events le ON g.event_id = le.id
WHERE g.is_featured = true OR g.event_id IS NOT NULL
ORDER BY g.created_at DESC;
```

### Approved Tributes View
```sql
CREATE VIEW approved_tributes AS
SELECT 
    id,
    author_name,
    relation_to_deceased,
    message,
    candle_lit,
    created_at
FROM tributes
WHERE approved = true
ORDER BY created_at DESC;
```

## Stored Procedures

### Get Life Events with Gallery Count
```sql
CREATE OR REPLACE FUNCTION get_life_events_with_gallery_count(
    p_limit INTEGER DEFAULT 100,
    p_offset INTEGER DEFAULT 0
)
RETURNS TABLE (
    id UUID,
    event_year INTEGER,
    title VARCHAR(255),
    description TEXT,
    location_name VARCHAR(255),
    coordinates POINT,
    is_featured BOOLEAN,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE,
    gallery_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        le.id,
        le.event_year,
        le.title,
        le.description,
        le.location_name,
        le.coordinates,
        le.is_featured,
        le.created_at,
        le.updated_at,
        COUNT(g.id) as gallery_count
    FROM life_events le
    LEFT JOIN gallery g ON le.id = g.event_id
    GROUP BY le.id, le.event_year, le.title, le.description, le.location_name, le.coordinates, le.is_featured, le.created_at, le.updated_at
    ORDER BY le.event_year ASC
    LIMIT p_limit
    OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;
```

### Search All Content
```sql
CREATE OR REPLACE FUNCTION search_all_content(p_query TEXT)
RETURNS TABLE (
    type VARCHAR(20),
    id UUID,
    title VARCHAR(255),
    description TEXT,
    score REAL
) AS $$
BEGIN
    -- Search life events
    RETURN QUERY
    SELECT 
        'life_event' as type,
        le.id,
        le.title,
        le.description,
        ts_rank(to_tsvector('english', le.title || ' ' || COALESCE(le.description, '')), plainto_tsquery('english', p_query)) as score
    FROM life_events le
    WHERE to_tsvector('english', le.title || ' ' || COALESCE(le.description, '')) @@ plainto_tsquery('english', p_query)
    
    UNION ALL
    
    -- Search gallery
    SELECT 
        'gallery' as type,
        g.id,
        g.title,
        g.caption,
        ts_rank(to_tsvector('english', COALESCE(g.title, '') || ' ' || COALESCE(g.caption, '')), plainto_tsquery('english', p_query)) as score
    FROM gallery g
    WHERE to_tsvector('english', COALESCE(g.title, '') || ' ' || COALESCE(g.caption, '')) @@ plainto_tsquery('english', p_query)
    
    UNION ALL
    
    -- Search approved tributes
    SELECT 
        'tribute' as type,
        t.id,
        t.author_name,
        t.message,
        ts_rank(to_tsvector('english', t.author_name || ' ' || t.message), plainto_tsquery('english', p_query)) as score
    FROM tributes t
    WHERE t.approved = true 
    AND to_tsvector('english', t.author_name || ' ' || t.message) @@ plainto_tsquery('english', p_query)
    
    ORDER BY score DESC;
END;
$$ LANGUAGE plpgsql;
```

## Triggers

### Update Timestamp Trigger
```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_life_events_updated_at
    BEFORE UPDATE ON life_events
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### Notify on New Tribute
```sql
CREATE OR REPLACE FUNCTION notify_new_tribute()
RETURNS TRIGGER AS $$
BEGIN
    -- Send notification for real-time updates
    PERFORM pg_notify('new_tribute', 
        json_build_object(
            'id', NEW.id,
            'author_name', NEW.author_name,
            'message', NEW.message,
            'candle_lit', NEW.candle_lit,
            'approved', NEW.approved
        )::text
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tribute_insert_notify
    AFTER INSERT ON tributes
    FOR EACH ROW
    EXECUTE FUNCTION notify_new_tribute();
```

## Database Constraints

### Check Constraints
```sql
-- Additional constraints for data integrity
ALTER TABLE life_events ADD CONSTRAINT chk_event_year CHECK (event_year >= 1900 AND event_year <= EXTRACT(YEAR FROM NOW()) + 10);
ALTER TABLE gallery ADD CONSTRAINT chk_file_size CHECK (file_size > 0);
ALTER TABLE gallery ADD CONSTRAINT chk_dimensions CHECK (width > 0 AND height > 0);
ALTER TABLE tributes ADD CONSTRAINT chk_author_name CHECK (LENGTH(TRIM(author_name)) > 0);
ALTER TABLE tributes ADD CONSTRAINT chk_message CHECK (LENGTH(TRIM(message)) > 0);
```

### Foreign Key Constraints
```sql
-- Ensure referential integrity
ALTER TABLE gallery ADD CONSTRAINT fk_gallery_event_id 
    FOREIGN KEY (event_id) REFERENCES life_events(id) 
    ON DELETE SET NULL;
```

## Performance Optimization

### Materialized Views for Complex Queries
```sql
CREATE MATERIALIZED VIEW gallery_stats AS
SELECT 
    COUNT(*) as total_items,
    COUNT(CASE WHEN media_type = 'image' THEN 1 END) as image_count,
    COUNT(CASE WHEN media_type = 'video' THEN 1 END) as video_count,
    SUM(file_size) as total_file_size,
    AVG(file_size) as avg_file_size
FROM gallery;

-- Refresh periodically
CREATE OR REPLACE FUNCTION refresh_gallery_stats()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY gallery_stats;
END;
$$ LANGUAGE plpgsql;
```

### Partitioning for Large Tables
```sql
-- Partition tributes by year for better performance
CREATE TABLE tributes_2024 PARTITION OF tributes
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

CREATE TABLE tributes_2025 PARTITION OF tributes
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
```

## Backup and Maintenance

### Backup Strategy
```sql
-- Create backup user
CREATE USER backup_user WITH PASSWORD 'backup_password';
GRANT CONNECT ON DATABASE everbloom TO backup_user;
GRANT USAGE ON SCHEMA public TO backup_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO backup_user;

-- Backup script
-- pg_dump -h localhost -U backup_user -d everbloom > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Maintenance Tasks
```sql
-- Update statistics for query optimizer
ANALYZE;

-- Rebuild indexes for performance
REINDEX DATABASE everbloom;

-- Clean up old data (optional)
-- DELETE FROM tributes WHERE created_at < NOW() - INTERVAL '5 years' AND approved = false;
```

## Migration Scripts

### Initial Migration
```sql
-- This would be your first Alembic migration
-- alembic revision -m "Initial schema"

-- Content would be generated by Alembic based on the models
```

### Sample Data Migration
```sql
-- Create sample data for development
INSERT INTO life_events (event_year, title, description, location_name, is_featured) VALUES
(1950, 'Birth', 'The beginning of a beautiful journey', 'Nairobi, Kenya', true),
(1970, 'Education', 'Completed high school education', 'Nairobi, Kenya', false),
(1975, 'Career Start', 'Began teaching career', 'Nairobi, Kenya', true),
(1980, 'Marriage', 'Married soulmate', 'Nairobi, Kenya', true),
(1985, 'First Home', 'Bought first family home', 'Nairobi, Kenya', false),
(1990, 'Children', 'Blessed with wonderful children', 'Nairobi, Kenya', true),
(2000, 'Retirement', 'Retired from teaching', 'Nairobi, Kenya', true),
(2020, 'Grandchildren', 'Joy of becoming a grandmother', 'Nairobi, Kenya', true);
```

This comprehensive database schema provides a solid foundation for the memorial platform with proper relationships, indexing, and performance optimizations.
