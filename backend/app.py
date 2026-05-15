# backend/app.py - Simplified: Chatbot-only (TensorFlow removed for Render)
from __future__ import annotations
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import Gemini API for chatbot
try:
    import google.generativeai as genai
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        CHATBOT_ENABLED = True
    else:
        CHATBOT_ENABLED = False
        print("WARNING: GEMINI_API_KEY not found. Chatbot will be disabled.")
except ImportError:
    CHATBOT_ENABLED = False
    print("WARNING: google-generativeai not installed. Chatbot will be disabled.")

# Chatbot system prompt
SYSTEM_PROMPT = """
You are Caliber — a friendly and knowledgeable AI health assistant.

Your role:
- Give short, clear, and informative responses about health issues, wellness, and daily care.
- Provide concise tips, causes, and preventive steps for common symptoms or conditions.
- Keep explanations brief but meaningful — focus on clarity over length.
- Always include a quick precaution or self-care tip when relevant.
- If the user's issue seems serious, advise consulting a healthcare professional.
- Never diagnose diseases or recommend specific medicines.
- When asked non-medical questions, respond naturally as a helpful chatbot — clear, smart, and polite.

Response Style:
- Keep replies within 4–6 concise sentences or bullet points.
- Use simple language and friendly tone.
- Start with reassurance, then share tips or steps.
- End with a short reminder if needed (e.g., "See a doctor if it gets worse.").
- Avoid long paragraphs, technical jargon, or fear-based statements.
"""

# Initialize Gemini model if available
if CHATBOT_ENABLED:
    try:
        gemini_model = genai.GenerativeModel(
            model_name="gemini-1.5-flash-latest",
            system_instruction=SYSTEM_PROMPT
        )
    except Exception as e:
        print(f"Failed to initialize Gemini model: {e}")
        CHATBOT_ENABLED = False

# Pydantic models
class ChatIn(BaseModel):
    message: str

class ChatOut(BaseModel):
    reply: str

# FastAPI app
app = FastAPI(title="Caliber Food Detection API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint for Render"""
    return {
        "status": "healthy",
        "service": "caliber-backend",
        "chatbot_enabled": CHATBOT_ENABLED
    }

# Chatbot endpoint
@app.post("/api/chat")
def chat(req: ChatIn) -> ChatOut:
    """Chatbot endpoint using Google Gemini API"""
    if not CHATBOT_ENABLED:
        return ChatOut(reply="Chatbot is not available. Please set GEMINI_API_KEY environment variable.")
    
    if not req.message.strip():
        return ChatOut(reply="Please enter a message.")
    
    try:
        response = gemini_model.generate_content(req.message)
        return ChatOut(reply=response.text)
    except Exception as e:
        print(f"Chatbot error: {e}")
        return ChatOut(reply=f"Error: {str(e)}")

# Root endpoint
@app.get("/")
def root():
    """API info"""
    return {
        "name": "Caliber Food Detection API",
        "version": "1.0",
        "endpoints": {
            "health": "/health",
            "chat": "/api/chat",
            "docs": "/docs"
        }
    }

# OpenAPI docs
@app.get("/docs")
def swagger_ui():
    """Swagger UI documentation"""
    return {"docs": "Available at /docs"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
