# Everbloom Archive System Design

## Architecture Overview

The Everbloom Archive is a three-tier web application designed to create a scalable, interactive digital memorial platform.

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Database      │
│   (React/Vue)   │◄──►│   (FastAPI)     │◄──►│  (PostgreSQL)   │
│                 │    │                 │    │                 │
│ - Gallery       │    │ - REST API      │    │ - Life Events   │
│ - Timeline      │    │ - WebSocket     │    │ - Gallery       │
│ - Tributes      │    │ - File Upload   │    │ - Tributes      │
│ - Real-time     │    │ - Validation    │    │ - Relations     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Technology Stack

### Frontend
- **Framework**: React (Vite) or Vue.js
- **Styling**: Tailwind CSS
- **State Management**: Redux/Zustand
- **Real-time**: WebSocket Client
- **Animations**: Framer Motion/GSAP
- **Maps**: Mapbox/Leaflet (for Memory Map)

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL with PostGIS
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Authentication**: JWT (future)
- **File Storage**: Local filesystem (upgrade to S3/Cloudinary)
- **Real-time**: WebSocket

### Infrastructure
- **Deployment**: Docker/Docker Compose
- **Web Server**: Uvicorn
- **Database**: PostgreSQL 14+
- **File Storage**: Local (development), Cloud (production)
- **CDN**: CloudFront (production)

## Database Design

### Entity Relationship Diagram

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   life_events   │     │     gallery     │     │    tributes     │
├─────────────────┤     ├─────────────────┤     ├─────────────────┤
│ id (UUID) PK    │◄───┤ id (UUID) PK    │     │ id (UUID) PK    │
│ event_year      │     │ event_id FK     │     │ author_name     │
│ title           │     │ media_url       │     │ message         │
│ description     │     │ caption         │     │ candle_lit      │
│ location_name   │     │ is_featured     │     │ approved        │
│ coordinates     │     │ media_type      │     │ email           │
│ is_featured     │     │ title           │     │ created_at      │
│ created_at      │     │ description     │     └─────────────────┘
│ updated_at      │     │ file_size       │
└─────────────────┘     │ width           │
                        │ height          │
                        │ created_at      │
                        └─────────────────┘
```

### Indexes

```sql
-- Life Events
CREATE INDEX idx_life_events_year ON life_events(event_year);
CREATE INDEX idx_life_events_featured ON life_events(is_featured);
CREATE INDEX idx_life_events_location ON life_events USING GIST(coordinates);

-- Gallery
CREATE INDEX idx_gallery_event_id ON gallery(event_id);
CREATE INDEX idx_gallery_featured ON gallery(is_featured);
CREATE INDEX idx_gallery_type ON gallery(media_type);

-- Tributes
CREATE INDEX idx_tributes_approved ON tributes(approved);
CREATE INDEX idx_tributes_candle ON tributes(candle_lit);
CREATE INDEX idx_tributes_created ON tributes(created_at);
```

## API Design

### RESTful Endpoints

```
GET    /life-events          # List events with filtering
GET    /life-events/{id}     # Get specific event
POST   /life-events          # Create event
PUT    /life-events/{id}     # Update event
DELETE /life-events/{id}     # Delete event

GET    /gallery              # List gallery items
GET    /gallery/{id}         # Get specific item
POST   /gallery              # Upload item (multipart)
PUT    /gallery/{id}         # Update item
DELETE /gallery/{id}         # Delete item
GET    /uploads/{filename}   # Serve files

GET    /tributes             # List tributes (public)
GET    /tributes/{id}        # Get specific tribute
POST   /tributes             # Create tribute
POST   /tributes/{id}/light-candle  # Light candle
GET    /tributes/admin/pending      # Admin: pending tributes
POST   /tributes/{id}/approve       # Admin: approve tribute
PUT    /tributes/{id}        # Admin: update tribute
DELETE /tributes/{id}        # Admin: delete tribute

WS     /tributes/ws          # Real-time updates
```

### Response Formats

#### Success Response
```json
{
  "data": [...],
  "pagination": {
    "skip": 0,
    "limit": 100,
    "total": 250
  }
}
```

#### Error Response
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [...]
  }
}
```

## Real-time Architecture

### WebSocket Flow

```
Client A                     Server                     Client B
    │                          │                          │
    │─────────────────────────►│                          │
    │  Connect WebSocket       │                          │
    │◄─────────────────────────│                          │
    │  Connected               │                          │
    │                          │                          │
    │─────────────────────────►│                          │
    │  Light Candle            │                          │
    │◄─────────────────────────│                          │
    │  Success                 │                          │
    │                          │─────────────────────────►│
    │                          │  Broadcast Update        │
    │                          │◄─────────────────────────│
    │                          │  Acknowledged            │
    │                          │                          │
```

### Message Types

```typescript
interface WebSocketMessage {
  type: 'candle_lit' | 'tribute_approved' | 'new_tribute';
  data: {
    tribute_id: string;
    author_name: string;
    timestamp: string;
  };
}
```

## File Upload Architecture

### Upload Flow

```
Client                    FastAPI                    File System
  │                           │                           │
  │──────────────────────────►│                           │
  │  POST /gallery            │                           │
  │  (multipart/form-data)    │                           │
  │◄──────────────────────────│                           │
  │  202 Accepted             │                           │
  │                           │──────────────────────────►│
  │                           │  Save File                │
  │                           │◄──────────────────────────│
  │                           │  File Saved               │
  │                           │──────────────────────────►│
  │                           │  Create DB Record         │
  │                           │◄──────────────────────────│
  │                           │  Record Created           │
  │◄──────────────────────────│                           │
  │  201 Created              │                           │
```

### File Storage Strategy

**Development:**
- Local filesystem storage
- `/uploads` directory
- Served by FastAPI StaticFiles

**Production:**
- AWS S3 or Cloudinary
- CDN distribution
- Automatic image optimization
- Multiple format generation (WebP, AVIF)

## Performance Optimization

### Database Optimization

1. **Connection Pooling**: SQLAlchemy connection pool
2. **Query Optimization**: Indexed queries, pagination
3. **Caching**: Redis for frequently accessed data
4. **Read Replicas**: Separate read/write databases

### API Optimization

1. **Compression**: Gzip middleware
2. **Rate Limiting**: Prevent abuse
3. **CORS**: Properly configured
4. **Async Operations**: Non-blocking I/O

### Frontend Optimization

1. **Code Splitting**: Lazy loading components
2. **Image Optimization**: WebP format, lazy loading
3. **Caching**: Service worker for offline access
4. **Bundle Optimization**: Tree shaking, minification

## Security Considerations

### Authentication & Authorization

```python
# JWT Token Structure
{
  "sub": "user_id",
  "role": "admin|user",
  "exp": timestamp,
  "iat": timestamp
}
```

### Input Validation

- Pydantic schemas for all inputs
- File type validation
- SQL injection prevention (ORM)
- XSS prevention (content sanitization)

### File Security

- File type validation
- Size limits
- Virus scanning (production)
- Secure file naming

## Monitoring & Logging

### Application Metrics

- Request/response times
- Error rates
- Database query performance
- WebSocket connection counts

### Logging Strategy

```python
# Structured Logging
{
  "timestamp": "2024-01-01T00:00:00Z",
  "level": "INFO",
  "message": "Tribute created",
  "context": {
    "tribute_id": "uuid",
    "author": "John Doe",
    "ip": "192.168.1.1"
  }
}
```

### Health Checks

```python
GET /health
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## Deployment Architecture

### Docker Compose Setup

```yaml
version: '3.8'
services:
  frontend:
    build: ./frontend
    ports:
      - "8080:80"
    
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/everbloom
    
  database:
    image: postgres:14
    environment:
      - POSTGRES_DB=everbloom
    volumes:
      - postgres_data:/var/lib/postgresql/data
    
  redis:
    image: redis:7
    ports:
      - "6379:6379"
```

### Production Considerations

- **Load Balancer**: Nginx/HAProxy
- **SSL/TLS**: Let's Encrypt certificates
- **Backup Strategy**: Database snapshots, file backups
- **Disaster Recovery**: Multi-region deployment

## Scalability Plan

### Horizontal Scaling

1. **Backend**: Multiple FastAPI instances behind load balancer
2. **Database**: Read replicas, sharding
3. **File Storage**: Distributed object storage
4. **CDN**: Global content delivery

### Vertical Scaling

1. **Compute**: Larger instance sizes
2. **Memory**: Increased RAM for caching
3. **Storage**: Faster SSD storage
4. **Network**: Higher bandwidth

## Future Enhancements

### Phase 2 Features

1. **Audio Integration**: Voice recordings, favorite songs
2. **Video Support**: Video tributes, memorial videos
3. **Family Tree**: Genealogical connections
4. **Story Collaboration**: Multi-user story editing

### Phase 3 Features

1. **AI Integration**: Automated photo tagging, story suggestions
2. **Virtual Reality**: 3D memorial spaces
3. **Mobile Apps**: Native iOS/Android applications
4. **Internationalization**: Multi-language support

This system design provides a robust foundation for a memorial platform that can scale from a small family memorial to a large public archive while maintaining performance, security, and user experience.
