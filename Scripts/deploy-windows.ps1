# Everbloom Archive - Windows Deployment Script
# This script deploys the application for production use on Windows

Write-Host "🚀 Starting Everbloom Archive Production Deployment..." -ForegroundColor Green

# Colors for output
function Write-Status($message) {
    Write-Host "[INFO] $message" -ForegroundColor Green
}

function Write-Warning($message) {
    Write-Host "[WARNING] $message" -ForegroundColor Yellow
}

function Write-Error($message) {
    Write-Host "[ERROR] $message" -ForegroundColor Red
}

# Check if Docker is installed
try {
    docker --version | Out-Null
    Write-Status "Docker is installed"
} catch {
    Write-Error "Docker is not installed. Please install Docker Desktop first."
    exit 1
}

# Check if Docker Compose is installed
try {
    docker-compose --version | Out-Null
    Write-Status "Docker Compose is installed"
} catch {
    Write-Error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
}

# Check if .env.prod exists
if (-not (Test-Path ".env.prod")) {
    Write-Error ".env.prod file not found. Please create it from the template"
    exit 1
}

Write-Status "Environment file found"

# Create necessary directories
Write-Status "Creating necessary directories..."
New-Item -ItemType Directory -Force -Path "nginx\ssl" | Out-Null
New-Item -ItemType Directory -Force -Path "backend\backup" | Out-Null
New-Item -ItemType Directory -Force -Path "backend\logs" | Out-Null

# Build frontend
Write-Status "Building frontend..."
Set-Location frontend
npm ci --only=production --silent
npm run build
Set-Location ..

# Check SSL certificates
if (-not (Test-Path "nginx\ssl\cert.pem") -or -not (Test-Path "nginx\ssl\key.pem")) {
    Write-Warning "SSL certificates not found. Generating self-signed certificates..."
    
    # Create OpenSSL config if needed
    $opensslConfig = @"
[req]
distinguished_name = req_distinguished_name
x509_extensions = v3_req
prompt = no

[req_distinguished_name]
C = US
ST = State
L = City
O = Organization
CN = localhost

[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
"@
    
    $opensslConfig | Out-File -FilePath "openssl.conf" -Encoding ASCII
    
    # Generate self-signed certificate
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 `
        -keyout "nginx\ssl\key.pem" `
        -out "nginx\ssl\cert.pem" `
        -config "openssl.conf"
    
    Remove-Item "openssl.conf" -Force
    
    Write-Warning "Self-signed certificates generated. Replace with proper certificates for production."
}

# Stop existing containers
Write-Status "Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down

# Pull latest images
Write-Status "Pulling latest Docker images..."
docker-compose -f docker-compose.prod.yml pull

# Build custom images
Write-Status "Building custom Docker images..."
docker-compose -f docker-compose.prod.yml build

# Start services
Write-Status "Starting services..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to start
Write-Status "Waiting for services to start..."
Start-Sleep -Seconds 30

# Check service health
Write-Status "Checking service health..."
Start-Sleep -Seconds 10

$services = @("postgres", "backend", "nginx")
$healthyServices = @()

foreach ($service in $services) {
    $status = docker-compose -f docker-compose.prod.yml ps -q $service
    if ($status) {
        $health = docker inspect $status --format='{{.State.Health.Status}}' 2>$null
        if ($health -eq "healthy" -or $health -eq "") {
            Write-Status "$service is running"
            $healthyServices += $service
        } else {
            Write-Warning "$service may not be fully healthy yet"
        }
    } else {
        Write-Error "$service failed to start"
        docker-compose -f docker-compose.prod.yml logs $service
    }
}

# Test API endpoints
Write-Status "Testing API endpoints..."
$apiUrl = "https://localhost/api"

try {
    $response = Invoke-WebRequest -Uri "$apiUrl/health" -UseBasicParsing -SkipCertificateCheck
    if ($response.StatusCode -eq 200) {
        Write-Status "Backend API is responding correctly"
    } else {
        Write-Warning "Backend API returned status code: $($response.StatusCode)"
    }
} catch {
    Write-Warning "Backend API test failed: $($_.Exception.Message)"
}

# Display deployment information
Write-Host ""
Write-Status "🎉 Deployment completed!"
Write-Host ""
Write-Host "📋 Deployment Information:" -ForegroundColor Cyan
Write-Host "  - Frontend: https://localhost" -ForegroundColor White
Write-Host "  - Backend API: https://localhost/api" -ForegroundColor White
Write-Host "  - Admin Panel: https://localhost/admin" -ForegroundColor White
Write-Host "  - Health Check: https://localhost/api/health" -ForegroundColor White
Write-Host ""
Write-Host "🔧 Management Commands:" -ForegroundColor Cyan
Write-Host "  - View logs: docker-compose -f docker-compose.prod.yml logs -f [service]" -ForegroundColor White
Write-Host "  - Stop services: docker-compose -f docker-compose.prod.yml down" -ForegroundColor White
Write-Host "  - Restart services: docker-compose -f docker-compose.prod.yml restart" -ForegroundColor White
Write-Host ""
Write-Host "📁 Important Files:" -ForegroundColor Cyan
Write-Host "  - Environment: .env.prod" -ForegroundColor White
Write-Host "  - Nginx config: nginx\nginx.conf" -ForegroundColor White
Write-Host "  - SSL certs: nginx\ssl\" -ForegroundColor White
Write-Host "  - Backups: backend\backup\" -ForegroundColor White
Write-Host ""
Write-Warning "Remember to:"
Write-Warning "  - Replace self-signed SSL certificates with proper ones"
Write-Warning "  - Update yourdomain.com in nginx.conf"
Write-Warning "  - Monitor logs and service health regularly"
Write-Warning "  - Test the application thoroughly"
Write-Warning "  - Configure proper firewall rules"
Write-Host ""
Write-Status "Deployment is complete! 🚀"

# Show running services
Write-Host ""
Write-Host "📊 Current Services Status:" -ForegroundColor Cyan
docker-compose -f docker-compose.prod.yml ps
