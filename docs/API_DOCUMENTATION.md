# Everbloom Archive API Documentation

## Overview

The Everbloom Archive API is a FastAPI-based backend for managing a digital memorial archive. It provides endpoints for managing life events, gallery items, and tributes with real-time features.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not implement authentication. In a production environment, you should add JWT authentication for admin endpoints.

## Database Schema

### Life Events
- **id**: UUID (Primary Key)
- **event_year**: Integer (Year of the event)
- **title**: String (Event title)
- **description**: Text (Optional description)
- **location_name**: String (Optional location name)
- **coordinates**: POINT (PostGIS for geographical data)
- **is_featured**: Boolean (Whether to feature this event)
- **created_at**: DateTime
- **updated_at**: DateTime

### Gallery
- **id**: UUID (Primary Key)
- **event_id**: UUID (Foreign Key to Life Events)
- **media_url**: Text (URL to media file)
- **caption**: Text (Optional caption)
- **is_featured**: Boolean (Whether to feature this item)
- **media_type**: String ('image' or 'video')
- **title**: String (Optional title)
- **description**: Text (Optional description)
- **file_size**: Integer (File size in bytes)
- **width**: Integer (Media width)
- **height**: Integer (Media height)
- **created_at**: DateTime

### Tributes
- **id**: UUID (Primary Key)
- **author_name**: String (Name of tribute author)
- **relation_to_deceased**: String (Optional relationship)
- **message**: Text (Tribute message)
- **candle_lit**: Boolean (Whether candle is lit)
- **approved**: Boolean (Moderation status)
- **email**: String (Optional email for contact)
- **created_at**: DateTime

## API Endpoints

### Life Events

#### GET /life-events/
Get all life events with optional filtering.

**Query Parameters:**
- `skip`: Integer (default: 0) - Number of records to skip
- `limit`: Integer (default: 100, max: 1000) - Maximum records to return
- `featured`: Boolean - Filter for featured events only
- `year`: Integer - Filter by specific year
- `search`: String - Search in title, description, or location

**Response:**
```json
[
  {
    "id": "uuid",
    "event_year": 1950,
    "title": "Birth",
    "description": "Born in Nairobi",
    "location_name": "Nairobi, Kenya",
    "coordinates": null,
    "is_featured": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": null
  }
]
```

#### GET /life-events/{event_id}
Get a specific life event with associated gallery items.

#### POST /life-events/
Create a new life event.

**Request Body:**
```json
{
  "event_year": 1950,
  "title": "Birth",
  "description": "Born in Nairobi",
  "location_name": "Nairobi, Kenya",
  "coordinates": [-1.2921, 36.8219],
  "is_featured": true
}
```

#### PUT /life-events/{event_id}
Update a life event.

#### DELETE /life-events/{event_id}
Delete a life event.

### Gallery

#### GET /gallery/
Get all gallery items with optional filtering.

**Query Parameters:**
- `skip`: Integer (default: 0)
- `limit`: Integer (default: 100, max: 1000)
- `featured`: Boolean - Filter for featured items only
- `media_type`: String ('image' or 'video')
- `event_id`: String - Filter by life event
- `search`: String - Search in title, caption, or description

#### GET /gallery/{item_id}
Get a specific gallery item.

#### POST /gallery/
Upload a new gallery item.

**Request:** Multipart form data with file upload and metadata.

#### PUT /gallery/{item_id}
Update a gallery item.

#### DELETE /gallery/{item_id}
Delete a gallery item.

#### GET /uploads/{filename}
Serve uploaded files.

### Tributes

#### GET /tributes/
Get tributes with optional filtering.

**Query Parameters:**
- `skip`: Integer (default: 0)
- `limit`: Integer (default: 100, max: 1000)
- `approved_only`: Boolean (default: true) - Show only approved tributes
- `candles_only`: Boolean - Show only tributes with candles
- `search`: String - Search in author name or message

**Response (Public View):**
```json
[
  {
    "id": "uuid",
    "author_name": "John Doe",
    "relation_to_deceased": "Grandson",
    "message": "She was amazing...",
    "candle_lit": true,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

#### GET /tributes/{tribute_id}
Get a specific tribute (public view).

#### POST /tributes/
Create a new tribute (requires approval).

**Request Body:**
```json
{
  "author_name": "John Doe",
  "relation_to_deceased": "Grandson",
  "message": "She was amazing...",
  "candle_lit": false,
  "email": "john@example.com"
}
```

#### POST /tributes/{tribute_id}/light-candle
Light a candle for a tribute. This will broadcast a real-time update.

#### GET /tributes/admin/pending
Get pending tributes for moderation (admin only).

#### POST /tributes/{tribute_id}/approve
Approve a tribute (admin only).

#### PUT /tributes/{tribute_id}
Update a tribute (admin only).

#### DELETE /tributes/{tribute_id}
Delete a tribute (admin only).

#### WebSocket /tributes/ws
WebSocket endpoint for real-time updates (candle lighting, tribute approval).

## Real-time Features

### WebSocket Events

#### candle_lit
```json
{
  "type": "candle_lit",
  "tribute_id": "uuid",
  "author_name": "John Doe"
}
```

#### tribute_approved
```json
{
  "type": "tribute_approved",
  "tribute_id": "uuid",
  "author_name": "John Doe"
}
```

## Error Responses

All endpoints return appropriate HTTP status codes and error messages:

```json
{
  "detail": "Error message"
}
```

Common status codes:
- 400: Bad Request
- 404: Not Found
- 413: Payload Too Large (file uploads)
- 422: Validation Error

## File Upload

- Maximum file size: 10MB
- Supported formats: Images (JPG, PNG, WebP), Videos (MP4)
- Files are stored in `/uploads` directory
- Files are served at `/uploads/{filename}`

## Environment Variables

Create a `.env` file in the backend directory:

```env
DATABASE_URL=postgresql://user:password@localhost/everbloom
SECRET_KEY=your-secret-key-here
ALLOWED_ORIGINS=["http://localhost:8080", "http://172.24.208.1:8080"]
MAX_FILE_SIZE=10485760
UPLOAD_DIR=uploads
```

## Development Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up PostgreSQL database and update `DATABASE_URL`

3. Run database migrations:
```bash
alembic upgrade head
```

4. Start the server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
