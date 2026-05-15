# Caliber - Food Classification & Health Chatbot

## 🚀 Quick Start (Integrated Setup)

### Prerequisites
- **Python 3.11+**
- **Node.js 20+** and npm
- Git

### 🎯 Run Full Application (One Command)

#### Windows:
```bash
python app.py
```

#### Linux/Mac:
```bash
python app.py
```

#### Or manually:
```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r backend/requirements.txt
cd frontend && npm install && cd ..

# Run integrated app
python app.py
```

The application will:
1. ✅ Build the React frontend automatically
2. ✅ Start the FastAPI backend with ML model
3. ✅ Serve both on http://localhost:5000
4. ✅ Open your browser automatically

---

## 📦 Project Structure

```
project-root/
│
├── frontend/                       # React Frontend
│   ├── public/                     # Static assets
│   ├── src/                        # React source code
│   │   ├── pages/                 # Page components
│   │   │   ├── Camera.jsx        # Food detection
│   │   │   ├── ChatWidget.jsx    # Health chatbot
│   │   │   └── Lifestyle.jsx     # Lifestyle tracking
│   │   ├── components/            # Reusable components
│   │   └── App.jsx               # Main app component
│   ├── dist/                      # Built frontend (auto-generated)
│   ├── package.json              # Node dependencies
│   ├── vite.config.js            # Vite configuration
│   └── .env                       # Frontend environment variables
│
├── backend/                        # FastAPI Backend
│   ├── app.py                     # Main API server
│   ├── routes/                    # API route handlers
│   ├── models/                    # ML models & utilities
│   ├── food_classification_model.keras  # Trained model (77MB)
│   ├── requirements.txt           # Python dependencies
│   └── .env                       # Backend environment variables
│
├── app.py                         # 🔥 MAIN ENTRY POINT
├── render.yaml                    # Render.com deployment config
├── DEPLOY.md                      # Deployment instructions
├── README.md                      # This file
└── .gitignore                     # Git ignore rules
```

---

## 🛠️ Manual Setup (If needed)

### 1. Install Backend Dependencies
```bash
# Create virtual environment
python -m venv .venv

# Activate it
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install Python packages
pip install -r backend/requirements.txt
```

### 2. Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
npm run build
```

Frontend will run on: `http://localhost:5173`

## API Endpoints (Port 5000)

- `GET /` - API health check
- `POST /predict` - Upload image for food classification
- `POST /api/chat` - Send message to health chatbot

## Environment Variables

Create `.env` files in both directories:

**backend/.env:**
```
GEMINI_API_KEY=your_api_key_here
```

**frontend/.env:**
```
VITE_API_BASE=http://localhost:5000
```

## Features

### Food Classification
- Upload or capture food images
- Detect food items from 58 categories
- See top 5 predictions with confidence scores

### Health Chatbot
- Ask health and wellness questions
- Get symptoms advice and daily care tips
- Powered by Google Gemini AI

### Lifestyle Tracking
- Track daily activities and health metrics
- Personalized wellness recommendations

## Troubleshooting

### Backend not starting?
- Ensure Python 3.8+ is installed
- Check if port 5000 is available
- Verify all dependencies are installed: `pip install -r requirements.txt`

### Frontend not connecting?
- Ensure backend is running on port 5000
- Check browser console for errors
- Verify API_BASE is set to `http://localhost:5000`

### 404 Errors?
- Backend must be running BEFORE starting frontend
- Check terminal logs for errors
- Visit `http://localhost:5000` to verify backend is up

## Tech Stack

**Backend:**
- FastAPI
- TensorFlow/Keras
- Google Generative AI
- OpenCV, Pillow

**Frontend:**
- React 18
- Vite
- Lucide Icons
- Modern CSS

## Development

Both frontend and backend support hot-reload:
- Backend: Use `--reload` flag with uvicorn
- Frontend: Vite automatically hot-reloads

## License

MIT
cc