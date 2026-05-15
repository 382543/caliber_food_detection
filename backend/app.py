# backend/app.py - Pure Python WSGI app using Werkzeug + REST API (zero compiled deps)
import os
import json
import requests
from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Gemini API configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CHATBOT_ENABLED = bool(GEMINI_API_KEY)
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

if not CHATBOT_ENABLED:
    print("WARNING: GEMINI_API_KEY not found. Chatbot will be disabled.")

# Chatbot system prompt
SYSTEM_PROMPT = """You are Caliber - a friendly and knowledgeable AI health assistant. Give short, clear responses about health issues, wellness, and daily care. Keep replies within 4-6 concise sentences. Never diagnose diseases or recommend specific medicines."""


def call_gemini_api(message):
    """Call Google Generative AI REST API directly"""
    if not CHATBOT_ENABLED:
        return None
    
    try:
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": SYSTEM_PROMPT + "\n\nUser: " + message}
                    ]
                }
            ]
        }
        
        response = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if "candidates" in data and len(data["candidates"]) > 0:
                candidate = data["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    return candidate["content"]["parts"][0].get("text", "No response generated")
        
        return f"API Error: {response.status_code} - {response.text[:100]}"
    except Exception as e:
        return f"Error: {str(e)}"


def json_response(data, status=200):
    """Return JSON response"""
    return Response(
        json.dumps(data),
        status=status,
        mimetype="application/json"
    )


def application(environ, start_response):
    """WSGI application"""
    request = Request(environ)
    path = request.path
    method = request.method

    # Health check
    if path == "/health" and method == "GET":
        return json_response({
            "status": "healthy",
            "service": "caliber-backend",
            "chatbot_enabled": CHATBOT_ENABLED
        })(environ, start_response)

    # Chatbot endpoint
    if path == "/api/chat" and method == "POST":
        try:
            data = json.loads(request.get_data(as_text=True))
            message = data.get("message", "").strip()
            
            if not message:
                return json_response({"reply": "Please enter a message."}, 400)(environ, start_response)
            
            if not CHATBOT_ENABLED:
                return json_response({
                    "reply": "Chatbot is not available. Please set GEMINI_API_KEY."
                }, 503)(environ, start_response)
            
            reply = call_gemini_api(message)
            return json_response({"reply": reply})(environ, start_response)
        
        except Exception as e:
            print(f"Chatbot error: {e}")
            return json_response({"reply": f"Error: {str(e)}"}, 500)(environ, start_response)

    # Root endpoint
    if path == "/" and method == "GET":
        return json_response({
            "name": "Caliber Food Detection API",
            "version": "1.0",
            "endpoints": {
                "health": "/health",
                "chat": "/api/chat"
            }
        })(environ, start_response)

    # CORS preflight
    if method == "OPTIONS":
        response = Response("", status=204)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return response(environ, start_response)

    # 404 Not Found
    return json_response({"error": "Not Found"}, 404)(environ, start_response)


if __name__ == "__main__":
    # Development server
    port = int(os.getenv("PORT", 8000))
    print(f"Starting server on http://0.0.0.0:{port}")
    run_simple("0.0.0.0", port, application, use_debugger=True, use_reloader=True)
