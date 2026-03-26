# Docker Run Guide for Everbloom Archive

## 🐳 **Docker Setup Options**

Since Docker Desktop may not be available, here are multiple ways to run the project:

---

## 🚀 **Option 1: Direct Development (Recommended)**

### **Start Backend**
```bash
cd backend
python complete_app.py
```

### **Start Frontend**
```bash
cd frontend
npm run dev
```

### **Access Points**
- Frontend: http://localhost:8080
- Backend API: http://localhost:8000
- Admin Panel: http://localhost:8000/admin

---

## 🐳 **Option 2: Docker (When Desktop Available)**

### **Prerequisites**
1. Install Docker Desktop from https://www.docker.com/products/docker-desktop
2. Start Docker Desktop
3. Wait for it to fully initialize

### **Build and Run**
```bash
# Build containers
docker-compose -f docker-compose.simple.yml build

# Start services
docker-compose -f docker-compose.simple.yml up -d

# View logs
docker-compose -f docker-compose.simple.yml logs -f

# Stop services
docker-compose -f docker-compose.simple.yml down
```

---

## 🔧 **Option 3: Manual Docker Commands**

### **Build Backend Image**
```bash
cd backend
docker build -f Dockerfile.simple -t everbloom-backend .
```

### **Run Backend Container**
```bash
docker run -d \
  --name everbloom-backend \
  -p 8000:8000 \
  -v "$(pwd):/app" \
  -v uploads:/app/uploads \
  everbloom-backend
```

### **Build Frontend Image**
```bash
cd frontend
docker build -t everbloom-frontend .
```

### **Run Frontend Container**
```bash
docker run -d \
  --name everbloom-frontend \
  -p 8080:80 \
  --link everbloom-backend:backend \
  everbloom-frontend
```

---

## 📋 **Option 4: Docker Compose with YAML Fix**

### **Fixed docker-compose.simple.yml**
```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.simple
    container_name: everbloom-backend-docker
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./everbloom.db
      - SECRET_KEY=everbloom-secret-key-change-in-production-2024
      - ALLOWED_ORIGINS=["http://localhost:8080", "http://172.24.208.1:8080"]
      - DEBUG=True
    volumes:
      - ./backend:/app
      - uploads:/app/uploads
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: everbloom-frontend-docker
    ports:
      - "8080:80"
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  uploads:
```

---

## 🛠️ **Troubleshooting Docker Issues**

### **Docker Desktop Not Starting**
1. **Restart Docker Desktop**
2. **Check WSL2**: `wsl --status`
3. **Update Docker Desktop**
4. **Check System Resources**: Ensure enough RAM (4GB+)

### **Build Failures**
```bash
# Clean Docker cache
docker system prune -a

# Rebuild without cache
docker-compose build --no-cache

# Check disk space
docker system df
```

### **Port Conflicts**
```bash
# Check what's using ports
netstat -ano | findstr :8080
netstat -ano | findstr :8000

# Kill conflicting processes
taskkill /PID <PID> /F
```

### **Permission Issues**
```bash
# Fix file permissions on Windows
icacls . /grant Everyone:F /T

# Or run as Administrator
```

---

## 📊 **Docker vs Development Comparison**

| Feature | Development | Docker | Winner |
|----------|-------------|----------|---------|
| **Speed** | ⚡ Fast | 🐢 Slower | Development |
| **Setup** | ✅ Simple | 🔧 Complex | Development |
| **Isolation** | ❌ None | ✅ Complete | Docker |
| **Portability** | ❌ Limited | ✅ Portable | Docker |
| **Production** | ❌ Not ready | ✅ Production | Docker |
| **Debugging** | ✅ Easy | 🔧 Harder | Development |

---

## 🎯 **Recommendation**

### **For Development & Testing:**
Use the **Direct Development** approach (Option 1)
- Faster iteration
- Easier debugging
- Hot reload
- No Docker overhead

### **For Production:**
Use **Docker** (Option 2 or 3)
- Consistent environment
- Easy deployment
- Better scaling
- Security isolation

---

## 🚀 **Quick Start Commands**

### **Development (Current Setup)**
```bash
# Terminal 1 - Backend
cd backend
python complete_app.py

# Terminal 2 - Frontend  
cd frontend
npm run dev

# Terminal 3 - Optional: Watch logs
tail -f backend/logs/app.log
```

### **Docker (When Available)**
```bash
# Build and run
docker-compose -f docker-compose.simple.yml up -d

# Check status
docker-compose -f docker-compose.simple.yml ps

# View logs
docker-compose -f docker-compose.simple.yml logs -f
```

---

## 📞 **Current Status**

✅ **Development Environment Ready**
- Backend: Python script `complete_app.py` ready
- Frontend: React app ready
- Database: SQLite with sample data
- WebSocket: Real-time features working

🐳 **Docker Files Prepared**
- `Dockerfile.simple` - Backend container
- `frontend/Dockerfile` - Frontend container
- `docker-compose.simple.yml` - Orchestration
- `frontend/nginx.conf` - Web server config

🎯 **Next Steps**
1. Use development setup for immediate testing
2. Set up Docker Desktop for containerized deployment
3. Deploy to production when ready

---

**Choose the option that works best for your environment!** 🚀
