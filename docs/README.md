# Everbloom Archive Documentation

Welcome to the comprehensive documentation for the Everbloom Archive platform. This digital memorial system is designed to celebrate and preserve the memories of loved ones through an interactive, web-based experience.

## 📚 Documentation Structure

### Core Documentation
- [**API Documentation**](./API_DOCUMENTATION.md) - Complete REST API reference
- [**System Design**](./SYSTEM_DESIGN.md) - Architecture and technical design
- [**Database Schema**](./DATABASE_SCHEMA.md) - Database structure and queries
- [**Deployment Guide**](./DEPLOYMENT_GUIDE.md) - Production deployment instructions

### Quick Links
- **Frontend**: `../frontend/` - React/Vue application
- **Backend**: `../backend/` - FastAPI REST API
- **Database**: PostgreSQL with PostGIS

## 🏗️ Architecture Overview

The Everbloom Archive is a modern, full-stack web application built with:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Database      │
│   React/Vue     │◄──►│   FastAPI       │◄──►│  PostgreSQL     │
│                 │    │                 │    │                 │
│ • Gallery       │    │ • REST API      │    │ • Life Events   │
│ • Timeline      │    │ • WebSocket     │    │ • Gallery       │
│ • Tributes      │    │ • File Upload   │    │ • Tributes      │
│ • Real-time     │    │ • Validation    │    │ • PostGIS       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- PostgreSQL 14+ with PostGIS
- Node.js 18+
- Python 3.9+

### Local Development

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/everbloom-archive.git
cd everbloom-archive
```

2. **Start with Docker Compose:**
```bash
docker-compose up -d
```

3. **Access the applications:**
- Frontend: http://localhost:8080
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Manual Setup

#### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your database configuration
uvicorn app.main:app --reload
```

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## 📊 Key Features

### Core Functionality
- **Life Timeline**: Interactive chronological journey through significant life events
- **Media Gallery**: Rich photo and video gallery with categorization
- **Tribute Wall**: Community messages and condolences with moderation
- **Digital Candles**: Real-time candle lighting with WebSocket updates
- **Memory Map**: Geographical visualization of life events (PostGIS)

### Technical Features
- **Real-time Updates**: WebSocket integration for live interactions
- **File Upload**: Secure media upload with validation
- **Search**: Full-text search across all content
- **Responsive Design**: Mobile-first, accessible interface
- **Performance**: Optimized database queries and caching

## 🔧 Technology Stack

### Frontend
- **Framework**: React (Vite) or Vue.js
- **Styling**: Tailwind CSS
- **State Management**: Redux/Zustand
- **Animations**: Framer Motion
- **Maps**: Mapbox/Leaflet

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL + PostGIS
- **ORM**: SQLAlchemy
- **Authentication**: JWT (planned)
- **Real-time**: WebSocket

### Infrastructure
- **Containerization**: Docker
- **Web Server**: Uvicorn/Nginx
- **Database**: PostgreSQL 14+
- **File Storage**: Local/Cloud (S3)

## 📖 Detailed Documentation

### API Documentation
Complete REST API reference including:
- Endpoint specifications
- Request/response formats
- Authentication methods
- Error handling
- WebSocket events

[View API Documentation →](./API_DOCUMENTATION.md)

### System Design
In-depth technical architecture covering:
- Component interactions
- Data flow diagrams
- Security considerations
- Performance optimization
- Scalability planning

[View System Design →](./SYSTEM_DESIGN.md)

### Database Schema
Comprehensive database documentation:
- Table structures
- Relationships and constraints
- Indexes and performance
- Sample queries
- Migration scripts

[View Database Schema →](./DATABASE_SCHEMA.md)

### Deployment Guide
Production deployment instructions:
- Docker configuration
- Cloud deployment (AWS, DigitalOcean)
- SSL/HTTPS setup
- Monitoring and logging
- Backup strategies

[View Deployment Guide →](./DEPLOYMENT_GUIDE.md)

## 🗄️ Database Overview

### Core Tables

#### Life Events
Chronological milestones and significant events:
```sql
CREATE TABLE life_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_year INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    location_name VARCHAR(255),
    coordinates POINT,  -- PostGIS for maps
    is_featured BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### Gallery
Media files (photos, videos) associated with events:
```sql
CREATE TABLE gallery (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_id UUID REFERENCES life_events(id),
    media_url TEXT NOT NULL,
    caption TEXT,
    is_featured BOOLEAN DEFAULT FALSE,
    media_type VARCHAR(50) DEFAULT 'image',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### Tributes
User messages and condolences:
```sql
CREATE TABLE tributes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    author_name VARCHAR(100) NOT NULL,
    relation_to_deceased VARCHAR(100),
    message TEXT NOT NULL,
    candle_lit BOOLEAN DEFAULT FALSE,
    approved BOOLEAN DEFAULT FALSE,  -- Moderation
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 🌐 API Endpoints

### Life Events
- `GET /life-events/` - List events with filtering
- `POST /life-events/` - Create new event
- `GET /life-events/{id}` - Get specific event
- `PUT /life-events/{id}` - Update event
- `DELETE /life-events/{id}` - Delete event

### Gallery
- `GET /gallery/` - List media items
- `POST /gallery/` - Upload media file
- `GET /gallery/{id}` - Get specific item
- `PUT /gallery/{id}` - Update item
- `DELETE /gallery/{id}` - Delete item

### Tributes
- `GET /tributes/` - List approved tributes
- `POST /tributes/` - Create tribute (pending approval)
- `POST /tributes/{id}/light-candle` - Light candle
- `GET /tributes/admin/pending` - Get pending tributes
- `POST /tributes/{id}/approve` - Approve tribute

### WebSocket
- `WS /tributes/ws` - Real-time updates for candles and approvals

## 🔒 Security Features

### Data Protection
- Input validation with Pydantic schemas
- SQL injection prevention (ORM)
- File upload validation
- XSS protection

### Access Control
- Tribute moderation system
- Admin-only endpoints
- CORS configuration
- Rate limiting (planned)

### Privacy
- Sensitive data protection
- Secure file handling
- Email verification (planned)

## 📈 Performance Optimization

### Database Optimization
- Strategic indexing
- Query optimization
- Connection pooling
- Read replicas (planned)

### Application Performance
- Lazy loading
- Image optimization
- Caching strategies
- CDN integration (planned)

### Monitoring
- Health check endpoints
- Performance metrics
- Error tracking
- Usage analytics (planned)

## 🚀 Deployment Options

### Development
- Docker Compose
- Local database
- Hot reload
- Debug mode

### Production
- Docker containers
- Load balancing
- SSL/TLS encryption
- Database backups
- Monitoring and logging

## 🔄 Development Workflow

### Git Workflow
```
main (production)
├── develop (staging)
└── feature/feature-name
```

### Code Quality
- Type hints (Python)
- ESLint/Prettier (JavaScript)
- Database migrations (Alembic)
- API documentation (OpenAPI)

### Testing
- Unit tests (pytest)
- Integration tests
- API testing
- Frontend testing (planned)

## 🤝 Contributing

We welcome contributions to the Everbloom Archive project. Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Development Guidelines
- Follow code style conventions
- Write clear commit messages
- Update documentation
- Test your changes

## 📞 Support

### Documentation
- This documentation covers all aspects of the system
- API documentation includes examples
- Database schema with sample data
- Deployment instructions for various platforms

### Common Issues
- Database connection problems
- File upload errors
- CORS configuration
- SSL certificate issues

### Getting Help
- Check the troubleshooting sections
- Review the API documentation
- Examine the database schema
- Consult the deployment guide

## 📄 License

This project is licensed under the MIT License. See the LICENSE file for details.

## 🎯 Future Roadmap

### Phase 2 Features
- Audio integration (voice recordings, music)
- Video tributes and memorial videos
- Family tree connections
- Collaborative story editing

### Phase 3 Features
- AI-powered photo tagging
- Virtual reality memorial spaces
- Native mobile applications
- Multi-language support

### Infrastructure Improvements
- Cloud-native deployment
- Advanced analytics
- Enhanced security
- Global CDN distribution

---

This documentation serves as your comprehensive guide to understanding, developing, deploying, and maintaining the Everbloom Archive platform. Each section provides detailed information and practical examples to help you work effectively with the system.
