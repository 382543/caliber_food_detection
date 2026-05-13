# 🚀 Deployment Guide for Render

## What I Fixed

### 1. **Frontend API Connection**
- Updated [Camera.jsx](frontend/src/pages/Camera.jsx) and [ChatWidget.jsx](frontend/src/pages/ChatWidget.jsx)
- Now uses empty string for API_BASE in production → requests go to same domain
- Falls back to `localhost:5000` in development

### 2. **Backend Serves Frontend**
- Updated [backend/app.py](backend/app.py) to serve static files from `frontend/dist`
- Added `/health` endpoint for Render health checks
- Single service handles both API and frontend

### 3. **Environment Configuration**
- [.env.production](frontend/.env.production) set to empty (same-origin requests)
- [render.yaml](render.yaml) properly configured

---

## 📋 Pre-Deployment Checklist

### 1. **Build Frontend Locally (Test)**
```bash
cd frontend
npm install
npm run build
```
✅ Should create `frontend/dist` folder with `index.html` and `assets/`

### 2. **Test Backend Locally**
```bash
cd backend
python app.py
```
✅ Should see: "Frontend dist folder found" or similar message

### 3. **Test Full Stack Locally**
```bash
# Terminal 1: Start backend (it will serve frontend too)
cd backend
python app.py

# Open browser: http://localhost:5000
# Should show your React app
# Test camera and chatbot features
```

---

## 🌐 Deploy to Render

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Configure for Render deployment"
git push origin main
```

### Step 2: Create Web Service on Render
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **New +** → **Web Service**
3. Connect your GitHub repository
4. Use these settings:

| Setting | Value |
|---------|-------|
| **Name** | `caliber-health-app` |
| **Region** | Oregon (or closest to you) |
| **Branch** | `main` |
| **Root Directory** | (leave empty) |
| **Runtime** | `Python 3` |
| **Build Command** | See render.yaml (auto-detected) |
| **Start Command** | See render.yaml (auto-detected) |
| **Plan** | Free or Starter ($7/mo recommended for ML) |

### Step 3: Add Environment Variables
In Render Dashboard → Environment:

```
GEMINI_API_KEY=your_actual_api_key_here
PYTHON_VERSION=3.11.0
NODE_VERSION=20.10.0
```

> 🔑 Get Gemini API key from: https://aistudio.google.com/app/apikey

### Step 4: Deploy
1. Click **Create Web Service**
2. Wait 5-10 minutes for build (ML model is 77MB)
3. Once deployed, you'll get a URL like: `https://caliber-health-app.onrender.com`

---

## ✅ Post-Deployment Testing

### Test These Features:
1. **Home Page** → Should load with Caliber branding
2. **Camera Page** → Upload food image, should classify correctly
3. **Chatbot Widget** → Ask "i have pcod" → Should get health advice
4. **API Health** → Visit `/health` → Should return `{"status":"healthy"}`

### Troubleshooting:

**Issue: "Network error" in chatbot**
- Check if GEMINI_API_KEY is set in Render dashboard
- View logs: Render Dashboard → Logs tab

**Issue: 404 on frontend routes**
- Check if `frontend/dist` exists in build logs
- Verify build command completed successfully

**Issue: Model loading fails**
- Check if `food_classification_model.keras` exists in repo
- Free tier may run out of memory (upgrade to Starter plan)

---

## 🔄 Future Deployments

After initial setup, just push to GitHub:
```bash
git add .
git commit -m "Update feature"
git push
```

Render will auto-deploy if `autoDeploy: true` in render.yaml ✅

---

## 📊 Architecture

```
User Browser
     ↓
https://caliber-health-app.onrender.com
     ↓
FastAPI Backend (port $PORT)
     ├─ Serves: frontend/dist/* (React app)
     ├─ API: POST /predict (ML model)
     ├─ API: POST /api/chat (Gemini chatbot)
     └─ Health: GET /health
```

**Benefits:**
- ✅ Single service (cost-effective)
- ✅ No CORS issues (same origin)
- ✅ Simpler deployment
- ✅ One URL for everything

---

## 💡 Tips

1. **Monitor Usage**: Check Render dashboard for CPU/memory usage
2. **Logs**: Use Render logs to debug issues
3. **Custom Domain**: Add in Render → Settings → Custom Domain
4. **Auto-Deploy**: Enabled by default, disable if you want manual control

---

## 🆘 Need Help?

- Render Docs: https://render.com/docs
- Check logs in Render Dashboard
- Verify environment variables are set correctly
