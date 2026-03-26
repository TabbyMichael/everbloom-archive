# Railway Environment Variables Setup

## 📋 Required Environment Variables

Set these in your Railway dashboard under your backend service:

### 1. DATABASE_URL
**Purpose**: PostgreSQL database connection
**How to get**: 
1. In Railway dashboard, click on your PostgreSQL service
2. Copy the "Connection String" 
3. Paste it as the value

**Format**: 
```
postgresql://username:password@host.railway.app:5432/railway?sslmode=require
```

**Example**:
```
DATABASE_URL=postgresql://postgres:password://containers-us-west-xxx.railway.app:5432/railway
```

### 2. ALLOWED_ORIGINS
**Purpose**: CORS security - which frontend domains can access API
**Format**: Comma-separated list of your frontend URLs

**Examples**:
```
# For Vercel deployment
ALLOWED_ORIGINS=https://your-app.vercel.app

# For Netlify deployment  
ALLOWED_ORIGINS=https://your-app.netlify.app

# For multiple frontends
ALLOWED_ORIGINS=https://your-app.vercel.app,https://your-app.netlify.app,http://localhost:8080
```

**Important**: Include the full URL with protocol (https://)

### 3. SECRET_KEY
**Purpose**: JWT token signing and session security
**Format**: Any secure random string

**Generate one**:
```bash
# Using Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Using OpenSSL
openssl rand -base64 32
```

**Example**:
```
SECRET_KEY=your-super-secret-key-change-this-in-production
```

## 🔧 Optional Environment Variables

### PORT
**Purpose**: Railway automatically sets this
**Value**: `8000`
**Note**: Railway sets this automatically, but you can override if needed

### UPLOAD_DIR
**Purpose**: Directory for file uploads
**Value**: `/tmp/uploads`
**Note**: Railway uses ephemeral storage, use `/tmp` for uploads

### MAX_FILE_SIZE
**Purpose**: Maximum file upload size in bytes
**Value**: `10485760` (10MB)
**Note**: Adjust based on your needs

## 📝 Step-by-Step Setup

### In Railway Dashboard:

1. **Go to your backend service**
2. **Click "Variables" tab**
3. **Add each variable**:

#### Variable 1: DATABASE_URL
```
Name: DATABASE_URL
Value: postgresql://username:password@host.railway.app:5432/railway
Environment: Production
```

#### Variable 2: ALLOWED_ORIGINS  
```
Name: ALLOWED_ORIGINS
Value: https://your-frontend-domain.vercel.app
Environment: Production
```

#### Variable 3: SECRET_KEY
```
Name: SECRET_KEY
Value: your-generated-secret-key-here
Environment: Production
```

### Optional Variables:
```
Name: PORT
Value: 8000

Name: UPLOAD_DIR  
Value: /tmp/uploads

Name: MAX_FILE_SIZE
Value: 10485760
```

## 🚀 After Setting Variables

1. **Redeploy** your service to apply changes
2. **Check logs** to verify database connection
3. **Test endpoints**:
   - `https://your-project.railway.app/health`
   - `https://your-project.railway.app/`

## 🔍 Troubleshooting

### Database Connection Issues
- Verify DATABASE_URL is copied correctly from Railway PostgreSQL service
- Ensure `sslmode=require` is included
- Check that PostgreSQL service is running

### CORS Errors  
- Verify ALLOWED_ORIGINS includes your frontend URL
- Ensure URLs include `https://` protocol
- Check for typos in domain names

### Secret Key Issues
- Generate a new secure key if needed
- Ensure it's at least 32 characters long
- Don't use common words or patterns

## 📱 Testing Your Setup

### Health Check
```bash
curl https://your-project.railway.app/health
```

Should return:
```json
{
  "status": "healthy",
  "auth": "enabled", 
  "websocket": "enabled"
}
```

### API Test
```bash
curl https://your-project.railway.app/life-events
```

## ✅ Production Ready Checklist

- [ ] DATABASE_URL set with Railway PostgreSQL connection
- [ ] ALLOWED_ORIGINS includes all frontend domains  
- [ ] SECRET_KEY is a secure random string
- [ ] Service redeployed after setting variables
- [ ] Health endpoint returns success
- [ ] Frontend can successfully call API
- [ ] WebSocket connections work properly

Once these are configured, your Everbloom Archive backend will be fully operational on Railway! 🌸
