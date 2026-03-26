# Everbloom Archive Backend

A FastAPI-based backend for the Everbloom Archive memorial platform.

## Features

- **RESTful API** for life events, gallery, and tributes
- **Real-time updates** via WebSocket for candle lighting and tribute approvals
- **File upload** handling for images and videos
- **PostgreSQL** with PostGIS for geographical data
- **Database migrations** with Alembic
- **Comprehensive documentation** with OpenAPI/Swagger

## Quick Start

### Prerequisites

- Python 3.9+
- PostgreSQL 14+ with PostGIS extension
- Node.js (for frontend)

### Installation

1. **Clone and navigate to backend:**
```bash
cd backend
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up environment:**
```bash
cp .env.example .env
# Edit .env with your database URL and other settings
```

5. **Set up database:**
```bash
# Create database
createdb everbloom

# Enable PostGIS extension
psql everbloom -c "CREATE EXTENSION IF NOT EXISTS postgis;"

# Run migrations
alembic upgrade head
```

6. **Start the server:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

## Project Structure

```
backend/
├── app/
│   ├── api/              # API routers
│   │   ├── life_events.py
│   │   ├── gallery.py
│   │   └── tributes.py
│   ├── core/             # Core configuration
│   │   └── config.py
│   ├── crud/             # Database operations
│   │   ├── life_event.py
│   │   ├── gallery.py
│   │   └── tribute.py
│   ├── db/               # Database setup
│   │   └── database.py
│   ├── models/           # SQLAlchemy models
│   │   ├── life_event.py
│   │   ├── gallery.py
│   │   └── tribute.py
│   ├── schemas/          # Pydantic schemas
│   │   ├── life_event.py
│   │   ├── gallery.py
│   │   └── tribute.py
│   └── main.py           # FastAPI application
├── alembic/              # Database migrations
├── uploads/              # File upload directory
├── requirements.txt      # Python dependencies
├── alembic.ini          # Alembic configuration
└── .env.example         # Environment variables template
```

## API Endpoints

### Life Events
- `GET /life-events/` - List life events
- `POST /life-events/` - Create life event
- `GET /life-events/{id}` - Get specific event
- `PUT /life-events/{id}` - Update event
- `DELETE /life-events/{id}` - Delete event

### Gallery
- `GET /gallery/` - List gallery items
- `POST /gallery/` - Upload media file
- `GET /gallery/{id}` - Get specific item
- `PUT /gallery/{id}` - Update item
- `DELETE /gallery/{id}` - Delete item
- `GET /uploads/{filename}` - Serve uploaded files

### Tributes
- `GET /tributes/` - List approved tributes
- `POST /tributes/` - Create tribute (pending approval)
- `GET /tributes/{id}` - Get specific tribute
- `POST /tributes/{id}/light-candle` - Light candle
- `GET /tributes/admin/pending` - Get pending tributes (admin)
- `POST /tributes/{id}/approve` - Approve tribute (admin)

### WebSocket
- `WS /tributes/ws` - Real-time updates

## Database Migrations

### Create new migration:
```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply migrations:
```bash
alembic upgrade head
```

### Rollback migration:
```bash
alembic downgrade -1
```

## Development

### Running tests:
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

### Code formatting:
```bash
# Install development dependencies
pip install black isort flake8

# Format code
black app/
isort app/

# Lint code
flake8 app/
```

### Database operations:
```bash
# Create new migration after model changes
alembic revision --autogenerate -m "Add new field"

# Apply migration
alembic upgrade head

# Check current revision
alembic current

# View migration history
alembic history
```

## Configuration

### Environment Variables

See `.env.example` for all available options:

- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT secret key
- `ALLOWED_ORIGINS`: CORS allowed origins
- `MAX_FILE_SIZE`: Maximum upload file size (bytes)
- `UPLOAD_DIR`: Directory for uploaded files

### Database Setup

1. **Install PostgreSQL with PostGIS:**
```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib postgis

# macOS with Homebrew
brew install postgresql postgis

# Windows
# Download and install from official websites
```

2. **Create database and user:**
```sql
CREATE DATABASE everbloom;
CREATE USER everbloom_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE everbloom TO everbloom_user;
```

3. **Enable extensions:**
```sql
\c everbloom
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";
```

## Deployment

### Docker Deployment

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/everbloom
    depends_on:
      - db
    volumes:
      - ./uploads:/app/uploads

  db:
    image: postgis/postgis:14-3.2
    environment:
      - POSTGRES_DB=everbloom
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

### Production Considerations

1. **Security:**
   - Use strong `SECRET_KEY`
   - Enable HTTPS
   - Implement authentication
   - Validate all inputs

2. **Performance:**
   - Use connection pooling
   - Enable caching
   - Optimize database queries
   - Use CDN for static files

3. **Monitoring:**
   - Set up logging
   - Monitor database performance
   - Track API metrics
   - Set up health checks

## API Usage Examples

### Create Life Event
```bash
curl -X POST "http://localhost:8000/life-events/" \
  -H "Content-Type: application/json" \
  -d '{
    "event_year": 1950,
    "title": "Birth",
    "description": "Born in Nairobi",
    "location_name": "Nairobi, Kenya",
    "coordinates": [-1.2921, 36.8219],
    "is_featured": true
  }'
```

### Upload Gallery Item
```bash
curl -X POST "http://localhost:8000/gallery/" \
  -F "file=@photo.jpg" \
  -F "title=Family Photo" \
  -F "caption=Beautiful memories" \
  -F "is_featured=true"
```

### Create Tribute
```bash
curl -X POST "http://localhost:8000/tributes/" \
  -H "Content-Type: application/json" \
  -d '{
    "author_name": "John Doe",
    "relation_to_deceased": "Grandson",
    "message": "She was amazing...",
    "candle_lit": false,
    "email": "john@example.com"
  }'
```

### Light Candle
```bash
curl -X POST "http://localhost:8000/tributes/{tribute_id}/light-candle"
```

## Troubleshooting

### Common Issues

1. **Database connection error:**
   - Check PostgreSQL is running
   - Verify DATABASE_URL in .env
   - Ensure database exists

2. **Migration errors:**
   - Check database permissions
   - Verify PostGIS extension is enabled
   - Run `alembic stamp head` if needed

3. **File upload errors:**
   - Check uploads directory permissions
   - Verify MAX_FILE_SIZE setting
   - Ensure sufficient disk space

4. **CORS errors:**
   - Update ALLOWED_ORIGINS in .env
   - Check frontend URL matches allowed origins

### Debug Mode

Enable debug logging:
```bash
export DEBUG=True
uvicorn app.main:app --reload --log-level debug
```

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

## License

This project is licensed under the MIT License.
