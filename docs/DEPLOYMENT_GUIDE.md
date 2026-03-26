# Everbloom Archive - Deployment Guide

## 🚀 **Deploy to Vercel and Netlify**

This guide will help you deploy the Everbloom Archive frontend to popular hosting platforms.

---

## 📋 **Prerequisites**

### **Required Accounts**
- [ ] Vercel account (https://vercel.com)
- [ ] Netlify account (https://netlify.com)
- [ ] GitHub repository with code pushed

### **Backend Deployment Options**
1. **Render.com** (Recommended for Flask backend)
2. **Railway.app** (Easy deployment)
3. **Heroku** (Classic option)
4. **DigitalOcean** (Full control)

---

## 🌐 **Vercel Deployment**

### **Step 1: Install Vercel CLI**
```bash
npm install -g vercel
```

### **Step 2: Login to Vercel**
```bash
vercel login
```

### **Step 3: Deploy Frontend**
```bash
cd frontend
npm run deploy:vercel
```

### **Vercel Configuration Files Created**
- ✅ `vercel.json` - Main configuration
- ✅ `frontend/vercel.config.js` - Build settings
- ✅ `package.json` - Deployment scripts

### **Environment Variables in Vercel**
Set these in Vercel dashboard:
- `VITE_API_URL`: Your backend API URL
- `VITE_WS_URL`: Your WebSocket URL

---

## 🌿 **Netlify Deployment**

### **Step 1: Install Netlify CLI**
```bash
npm install -g netlify-cli
```

### **Step 2: Login to Netlify**
```bash
netlify login
```

### **Step 3: Deploy Frontend**
```bash
cd frontend
npm run deploy:netlify
```

### **Netlify Configuration Files Created**
- ✅ `netlify.toml` - Main configuration
- ✅ `netlify/functions/api/index.js` - API proxy
- ✅ `package.json` - Deployment scripts

### **Environment Variables in Netlify**
Set these in Netlify dashboard:
- `VITE_API_URL`: Your backend API URL
- `VITE_WS_URL`: Your WebSocket URL

---

## 🔧 **Backend Deployment Options**

### **Option 1: Render.com (Recommended)**
1. **Create Account**: https://render.com
2. **Connect GitHub**: Link your repository
3. **Configure Service**:
   - **Name**: everbloom-backend
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python complete_app.py`
   - **Port**: 8000
4. **Add Environment Variables**:
   - `DATABASE_URL`: PostgreSQL connection string
   - `SECRET_KEY`: Your secret key
   - `ALLOWED_ORIGINS`: `["https://your-domain.vercel.app", "https://your-domain.netlify.app"]`

### **Option 2: Railway.app**
1. **Install Railway CLI**: `npm install -g @railway/cli`
2. **Login**: `railway login`
3. **Deploy**: `railway up`
4. **Configure**: Set environment variables in dashboard

### **Option 3: Heroku**
1. **Install Heroku CLI**: `npm install -g heroku`
2. **Login**: `heroku login`
3. **Create App**: `heroku create everbloom-backend`
4. **Deploy**: `git push heroku main`
5. **Configure**: `heroku config:set VAR=VALUE`

---

## 🔄 **API Integration Setup**

### **Frontend API Configuration**
Update `frontend/src/services/api.ts`:
```typescript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';
```

### **CORS Configuration**
In your backend, update allowed origins:
```python
ALLOWED_ORIGINS = [
    "https://your-domain.vercel.app",
    "https://your-domain.netlify.app",
    "https://your-custom-domain.com"
]
```

---

## 📱 **Mobile & Performance Optimization**

### **Build Optimization**
```bash
# For production builds
npm run build

# Check bundle size
npm run build --analyze
```

### **Service Worker Registration**
```typescript
// In frontend/src/main.tsx
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js');
  });
}
```

---

## 🔐 **Security & SSL**

### **HTTPS Only**
Both Vercel and Netlify provide:
- ✅ Automatic SSL certificates
- ✅ HTTPS by default
- ✅ CDN distribution
- ✅ DDoS protection

### **Security Headers**
Already configured in deployment files:
- ✅ X-Frame-Options: DENY
- ✅ X-Content-Type-Options: nosniff
- ✅ X-XSS-Protection
- ✅ CORS headers

---

## 📊 **Domain Configuration**

### **Custom Domain Setup**
1. **Vercel**: Add domain in Vercel dashboard
2. **Netlify**: Add domain in Netlify dashboard
3. **DNS Settings**: Point to provided nameservers
4. **SSL Certificate**: Auto-provided by both platforms

### **Subdomain Options**
- Vercel: `your-app.vercel.app`
- Netlify: `your-app.netlify.app`
- Custom: `your-domain.com`

---

## 🎯 **Deployment Commands Summary**

### **Vercel**
```bash
# One-time deployment
cd frontend
npm run deploy:vercel

# Automatic deployment on git push
vercel --prod
```

### **Netlify**
```bash
# One-time deployment
cd frontend
npm run deploy:netlify

# Continuous deployment
netlify deploy --prod --dir=dist
```

### **Backend (Render)**
```bash
# Connect GitHub and auto-deploy
# Or manual deployment
git push origin main
```

---

## 📈 **Performance Monitoring**

### **Vercel Analytics**
- Built-in speed insights
- Real user monitoring
- Performance metrics
- Error tracking

### **Netlify Analytics**
- Site performance metrics
- Build monitoring
- Form submissions
- Bandwidth usage

### **Third-party Options**
- **Google Analytics**: Add tracking ID
- **Sentry**: Error monitoring
- **SpeedCurve**: Performance tracking

---

## 🔄 **CI/CD Pipeline**

### **GitHub Actions Workflow**
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy-vercel:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npm run build:vercel
      - uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.ORG_ID }}
          vercel-project-id: ${{ secrets.PROJECT_ID }}
```

---

## 🎊 **Deployment Checklist**

### **Pre-Deployment**
- [ ] Backend deployed and accessible
- [ ] Environment variables set
- [ ] CORS configured for domains
- [ ] Database migrated
- [ ] SSL certificates working

### **Post-Deployment**
- [ ] Frontend loads correctly
- [ ] API endpoints respond
- [ ] WebSocket connections work
- [ ] Forms submit successfully
- [ ] Images upload properly
- [ ] Mobile responsive
- [ ] Performance optimized

### **Testing**
- [ ] Test on multiple browsers
- [ ] Test on mobile devices
- [ ] Test real-time features
- [ ] Test admin panel
- [ ] Load testing

---

## 🛠️ **Troubleshooting**

### **Common Issues**
1. **CORS Errors**: Check allowed origins in backend
2. **WebSocket Issues**: Verify WebSocket URL
3. **Build Failures**: Check environment variables
4. **API 404s**: Verify proxy configuration

### **Debug Steps**
```bash
# Check build locally
npm run build

# Test API endpoints
curl https://your-backend-url.com/health

# Check WebSocket
wscat -c wss://your-backend-url.com
```

---

## 🎯 **Recommended Production Stack**

### **Frontend**
- **Platform**: Vercel or Netlify
- **Domain**: Custom domain with SSL
- **CDN**: Built-in distribution
- **Analytics**: Platform monitoring

### **Backend**
- **Platform**: Render.com
- **Database**: PostgreSQL
- **Monitoring**: Platform metrics
- **Backup**: Automated

### **Total Cost**
- **Frontend**: Free tier (Vercel/Netlify)
- **Backend**: ~$7-25/month (Render)
- **Database**: ~$5-15/month (PostgreSQL)
- **Total**: ~$12-40/month

---

## 🎊 **Deployment Success!**

🌸 **Your Everbloom Archive will be live and accessible worldwide!**

### **What You Get**
- Global CDN distribution
- Automatic SSL certificates
- 99.9% uptime SLA
- Performance monitoring
- Easy domain management
- Scalable infrastructure

### **Next Steps**
1. **Deploy Backend** to Render.com or Railway
2. **Deploy Frontend** to Vercel or Netlify
3. **Update Environment Variables** with live URLs
4. **Test All Features** on live domain
5. **Share with Family** and friends

**Your memorial platform will be ready to honor and celebrate life 24/7!** 🌸

---

*Choose the deployment option that best fits your needs and budget.*
