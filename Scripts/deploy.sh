#!/bin/bash

# Everbloom Archive Production Deployment Script
# This script deploys the application to production with PostgreSQL

set -e

echo "🚀 Starting Everbloom Archive Production Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if .env.prod exists
if [ ! -f .env.prod ]; then
    print_error ".env.prod file not found. Please create it from .env.prod.example"
    exit 1
fi

# Load environment variables
source .env.prod

# Validate required environment variables
required_vars=("POSTGRES_PASSWORD" "SECRET_KEY" "REDIS_PASSWORD")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        print_error "Required environment variable $var is not set in .env.prod"
        exit 1
    fi
done

print_status "Environment variables validated"

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p nginx/ssl
mkdir -p backend/backup
mkdir -p backend/logs

# Build frontend
print_status "Building frontend..."
cd frontend
npm ci --only=production
npm run build
cd ..

# Check SSL certificates
if [ ! -f nginx/ssl/cert.pem ] || [ ! -f nginx/ssl/key.pem ]; then
    print_warning "SSL certificates not found. Generating self-signed certificates..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/ssl/key.pem \
        -out nginx/ssl/cert.pem \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
    print_warning "Self-signed certificates generated. Replace with proper certificates for production."
fi

# Stop existing containers
print_status "Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down

# Pull latest images
print_status "Pulling latest Docker images..."
docker-compose -f docker-compose.prod.yml pull

# Build custom images
print_status "Building custom Docker images..."
docker-compose -f docker-compose.prod.yml build

# Start services
print_status "Starting services..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for database to be ready
print_status "Waiting for database to be ready..."
sleep 30

# Run database migrations
print_status "Running database migrations..."
docker-compose -f docker-compose.prod.yml exec backend python create_db.py

# Check service health
print_status "Checking service health..."
sleep 10

services=("postgres" "redis" "backend" "nginx")
for service in "${services[@]}"; do
    if docker-compose -f docker-compose.prod.yml ps | grep -q "$service.*Up"; then
        print_status "$service is running"
    else
        print_error "$service failed to start"
        docker-compose -f docker-compose.prod.yml logs $service
        exit 1
    fi
done

# Test API endpoints
print_status "Testing API endpoints..."
api_url="https://localhost/api"

if curl -k -s "$api_url/health" | grep -q "healthy"; then
    print_status "Backend API is responding correctly"
else
    print_error "Backend API is not responding correctly"
    exit 1
fi

# Setup backup cron job
print_status "Setting up backup cron job..."
backup_script="/usr/local/bin/everbloom-backup.sh"
cat << EOF | sudo tee $backup_script
#!/bin/bash
# Backup script for Everbloom Archive

# Backup database
docker-compose -f /path/to/everbloom-archive/docker-compose.prod.yml exec -T postgres pg_dump -U \$POSTGRES_USER \$POSTGRES_DB > /path/to/backups/everbloom-\$(date +%Y%m%d_%H%M%S).sql

# Clean old backups (keep last 30 days)
find /path/to/backups -name "everbloom-*.sql" -mtime +30 -delete
EOF

sudo chmod +x $backup_script

# Add to cron (runs daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * $backup_script") | crontab -

print_status "Backup cron job configured"

# Display deployment information
echo ""
print_status "🎉 Deployment completed successfully!"
echo ""
echo "📋 Deployment Information:"
echo "  - Frontend: https://yourdomain.com"
echo "  - Backend API: https://yourdomain.com/api"
echo "  - Health Check: https://yourdomain.com/api/health"
echo ""
echo "🔧 Management Commands:"
echo "  - View logs: docker-compose -f docker-compose.prod.yml logs -f [service]"
echo "  - Stop services: docker-compose -f docker-compose.prod.yml down"
echo "  - Restart services: docker-compose -f docker-compose.prod.yml restart"
echo ""
echo "📁 Important Files:"
echo "  - Environment: .env.prod"
echo "  - Nginx config: nginx/nginx.conf"
echo "  - SSL certs: nginx/ssl/"
echo "  - Backups: backend/backup/"
echo ""
print_warning "Remember to:"
echo "  - Replace self-signed SSL certificates with proper ones"
echo "  - Update yourdomain.com in nginx.conf"
echo "  - Monitor logs and service health regularly"
echo "  - Test the application thoroughly"
echo ""
print_status "Deployment is complete! 🚀"
