# Railway Deployment Guide

## 🚀 Deploy Everbloom Archive Backend to Railway

This guide will help you deploy the Everbloom Archive backend to Railway.app.

### Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Repository**: Your code should be pushed to GitHub
3. **Railway CLI** (optional): `npm install -g @railway/cli`

### Step 1: Prepare Your Repository

Your backend should now have these Railway-specific files:

```
backend/
├── Procfile                 # Railway process definition
├── railway.toml            # Railway configuration
├── requirements.railway.txt # Railway dependencies
├── start_railway.py        # Railway startup script
├── complete_app.py         # Main application (modified)
└── .env                    # Environment variables
```

### Step 2: Configure Environment Variables

Create/update your `.env` file:

```env
# Railway Configuration
PORT=8000
PYTHON_VERSION=3.9

# Database (Railway provides PostgreSQL)
DATABASE_URL=postgresql://username:password@host:port/database

# CORS (update with your frontend URL)
ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app,https://your-frontend-domain.netlify.app

# Security
SECRET_KEY=your-secret-key-here

# File Upload
UPLOAD_DIR=/tmp/uploads
MAX_FILE_SIZE=10485760
```

### Step 3: Deploy via Railway Dashboard

1. **Login to Railway**: [railway.app](https://railway.app)

2. **Click "New Project"** → "Deploy from GitHub repo"

3. **Select your repository** that contains the Everbloom Archive

4. **Configure the service**:
   - **Name**: `everbloom-backend`
   - **Environment**: `Python`
   - **Root Directory**: `backend/`
   - **Build Command**: `pip install -r requirements.railway.txt`
   - **Start Command**: `python start_railway.py`

5. **Add Environment Variables** in Railway dashboard:
   ```
   PORT=8000
   DATABASE_URL=your-postgres-connection-string
   ALLOWED_ORIGINS=https://your-frontend-url.vercel.app
   SECRET_KEY=your-secret-key
   ```

6. **Click "Deploy"**

### Step 4: Deploy via Railway CLI (Alternative)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Navigate to backend directory
cd backend

# Initialize Railway project
railway init

# Deploy
railway up

# Set environment variables
railway variables set PORT=8000
railway variables set DATABASE_URL=your-postgres-url
railway variables set ALLOWED_ORIGINS=https://your-frontend-url.vercel.app
```

### Step 5: Configure Database

Railway automatically provides a PostgreSQL database. Update your connection:

1. **Get Database URL**: In Railway dashboard, click on your PostgreSQL service
2. **Copy the connection string**
3. **Update Environment Variables**: Set `DATABASE_URL` to the connection string

### Step 6: Verify Deployment

Once deployed, your API will be available at:
```
https://your-project-name.railway.app
```

Test these endpoints:
- `GET /health` - Health check
- `GET /` - API information
- `GET /life-events` - List life events

### Step 7: Update Frontend Configuration

Update your frontend to use the Railway backend URL:

```typescript
// In frontend/src/services/api.ts
const API_BASE_URL = 'https://your-project-name.railway.app';
```

### Environment Variables for Production

Set these in Railway dashboard:

```env
# Required
PORT=8000
DATABASE_URL=postgresql://user:pass@host:port/db

# Security
SECRET_KEY=your-production-secret-key

# CORS (comma-separated)
ALLOWED_ORIGINS=https://yourdomain.vercel.app,https://yourdomain.netlify.app

# Optional
UPLOAD_DIR=/tmp/uploads
MAX_FILE_SIZE=10485760
PYTHON_VERSION=3.9
```

### Troubleshooting

#### Common Issues

1. **Build Failures**:
   - Check `requirements.railway.txt` has correct dependencies
   - Verify `Procfile` points to correct startup script

2. **Database Connection**:
   - Ensure `DATABASE_URL` is correctly set
   - Check PostgreSQL service is running in Railway

3. **CORS Errors**:
   - Update `ALLOWED_ORIGINS` with your frontend URL
   - Ensure frontend URL includes protocol (https://)

4. **Port Issues**:
   - Railway automatically assigns ports
   - Use `PORT` environment variable in your code

#### Debug Commands

```bash
# View logs
railway logs

# View variables
railway variables

# Redeploy
railway up

# Open in browser
railway open
```

### Railway Configuration Files Explained

#### `Procfile`
```
web: python start_railway.py
```
- Tells Railway how to start your application

#### `railway.toml`
```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "python start_railway.py"
restartPolicyType = "ON_FAILURE"

[env]
PORT = "8000"
PYTHON_VERSION = "3.9"
```
- Railway-specific configuration
- Defines build and deployment settings

#### `requirements.railway.txt`
```
flask==3.1.3
flask-cors==6.0.2
flask-socketio==5.6.1
python-dotenv==1.0.0
werkzeug==3.1.7
cryptography==46.0.6
gunicorn==21.2.0
```
- Minimal dependencies for Railway deployment

### Production Considerations

1. **Database Backups**: Railway automatically backs up PostgreSQL
2. **SSL**: Railway provides HTTPS automatically
3. **Monitoring**: Use Railway's built-in monitoring
4. **Scaling**: Railway supports horizontal scaling

### Next Steps

1. **Deploy Frontend**: Deploy your frontend to Vercel/Netlify
2. **Update CORS**: Add your frontend URL to `ALLOWED_ORIGINS`
3. **Test Integration**: Ensure frontend can communicate with backend
4. **Monitor**: Check Railway logs for any issues

### Success!

Your Everbloom Archive backend is now running on Railway and ready to serve your memorial platform! 🌸

For support, check the [Railway documentation](https://docs.railway.app/) or review the logs in your Railway dashboard.
