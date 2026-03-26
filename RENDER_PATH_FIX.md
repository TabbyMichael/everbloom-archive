# Render Path Issue Fix

## 🚨 Issue Identified

Render is looking for `requirements.txt` in the **root directory**, but your file is in `backend/requirements.txt`. Render can't find it because:

```
❌ Wrong: /requirements.txt (doesn't exist)
✅ Correct: /backend/requirements.txt (exists)
```

## ✅ Solutions

### Option 1: Use `render.yaml` (Recommended)

I've created `render.yaml` in your root directory with the correct configuration:

```yaml
services:
  - type: web
    name: everbloom-backend
    env: python
    plan: free
    repo: https://github.com/TabbyMichael/everbloom-archive
    rootDir: backend          # 👈 This tells Render to look in backend/
    buildCommand: pip install -r requirements.txt
    startCommand: python start_railway.py
    healthCheckPath: /health
    envVars:
      - key: PORT
        value: 8000
      - key: PYTHON_VERSION
        value: 3.9
```

### Option 2: Move requirements.txt to root

If you prefer not to use `render.yaml`:

```bash
# Copy requirements.txt to root
cp backend/requirements.txt ./requirements.txt
```

### Option 3: Update Render Dashboard Settings

In your Render service settings:
- **Root Directory**: `backend`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python start_railway.py`

## 🚀 Next Steps

### Using render.yaml (Easiest):

1. **Commit and push** the new `render.yaml` file
2. **Redeploy** on Render (it will automatically use the config)
3. **Set environment variables** in Render dashboard:
   ```
   DATABASE_URL=your-render-postgres-connection
   ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app
   SECRET_KEY=your-secret-key
   ```

### Using Dashboard Settings:

1. Go to your Render service → **Settings**
2. **Build & Deploy** section:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python start_railway.py`
3. **Redeploy**
4. Set environment variables

## 📋 Why This Happens

Render looks for files based on the **root directory** setting:
- **Default**: Root directory (`/`)
- **With `rootDir: backend`**: Backend directory (`/backend/`)

When `rootDir` is not set, it looks in `/requirements.txt` which doesn't exist.

## ✅ Expected Result

After fixing the path:
- ✅ **Build Success**: Render finds `requirements.txt` in `backend/`
- ✅ **Dependencies Install**: Flask packages installed correctly
- ✅ **App Starts**: `start_railway.py` runs from backend directory
- ✅ **Health Check**: `/health` endpoint responds

## 🔍 render.yaml Benefits

- **Automatic Configuration**: No manual dashboard settings needed
- **Version Control**: Configuration tracked in Git
- **Environment Variables**: Predefined structure for secrets
- **Reproducible**: Same config works across deployments

## 📝 Complete File Structure

```
everbloom-archive/
├── render.yaml              # ✅ Created - Render configuration
├── backend/
│   ├── requirements.txt     # ✅ Flask dependencies
│   ├── start_railway.py      # ✅ Startup script
│   ├── complete_app.py       # ✅ Main Flask app
│   └── ...
└── ...
```

Your Everbloom Archive should now deploy successfully to Render! 🌸

Choose Option 1 (render.yaml) for the easiest fix!
