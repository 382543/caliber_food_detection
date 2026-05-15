# backend/app.py - Pure Python WSGI app using Werkzeug (zero compiled deps)
import os
import json
from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
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
- If the user''s issue seems serious, advise consulting a healthcare professional.
- Never diagnose diseases or recommend specific medicines.

Response Style:
- Keep replies within 4–6 concise sentences or bullet points.
- Use simple language and friendly tone.
- Start with reassurance, then share tips or steps.
- End with a short reminder if needed.
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
            
            response = gemini_model.generate_content(message)
            return json_response({"reply": response.text})(environ, start_response)
        
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
