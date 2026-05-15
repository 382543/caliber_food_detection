"""
Caliber Food Classification & Health Chatbot - Integrated Application
Runs both Backend (pure Python WSGI) and serves Frontend (React build)
"""
import os
import sys
import subprocess
import webbrowser
from pathlib import Path
from threading import Thread
import time

# Add backend to Python path
BACKEND_DIR = Path(__file__).parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

# Import the WSGI application from backend
from backend.app import application
from werkzeug.wsgi import wrap_file
from werkzeug.wrappers import Response
from werkzeug.serving import run_simple

# Configuration
HOST = "127.0.0.1"
PORT = 5000
FRONTEND_DIR = Path(__file__).parent / "frontend"
FRONTEND_DIST = FRONTEND_DIR / "dist"


def build_frontend():
    """Build React frontend if not already built"""
    print("\n" + "="*60)
    print("🔨 Checking Frontend Build...")
    print("="*60)
    
    if FRONTEND_DIST.exists():
        print("✅ Frontend already built - skipping rebuild!")
        return True
    
    print("📦 Attempting to build frontend...")
    
    try:
        subprocess.run(["npm", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  npm not found. Install Node.js from https://nodejs.org/")
        return False
    
    node_modules = FRONTEND_DIR / "node_modules"
    if not node_modules.exists():
        print("📥 Installing npm dependencies...")
        try:
            subprocess.run(["npm", "install"], cwd=FRONTEND_DIR, check=True, capture_output=True)
            print("✅ Dependencies installed!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    
    try:
        subprocess.run(["npm", "run", "build"], cwd=FRONTEND_DIR, check=True, capture_output=True)
        print("✅ Frontend built successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Frontend build failed: {e}")
        return False


def serve_static_file(path):
    """Serve a static file from frontend/dist"""
    file_path = FRONTEND_DIST / path
    if file_path.exists() and file_path.is_file():
        with open(file_path, 'rb') as f:
            response = Response(wrap_file({}, f), mimetype='application/octet-stream')
            
            # Set appropriate content-type
            if path.endswith('.html'):
                response.mimetype = 'text/html'
            elif path.endswith('.css'):
                response.mimetype = 'text/css'
            elif path.endswith('.js'):
                response.mimetype = 'application/javascript'
            elif path.endswith('.json'):
                response.mimetype = 'application/json'
            elif path.endswith('.png'):
                response.mimetype = 'image/png'
            elif path.endswith('.jpg') or path.endswith('.jpeg'):
                response.mimetype = 'image/jpeg'
            elif path.endswith('.svg'):
                response.mimetype = 'image/svg+xml'
            
            return response(None, lambda: None)
    return None


def create_integrated_app():
    """Create integrated WSGI app that serves both backend and frontend"""
    from werkzeug.wrappers import Request, Response
    import json
    
    def integrated_application(environ, start_response):
        """Integrated WSGI app: backend API + frontend static files"""
        request = Request(environ)
        path = request.path
        
        # Route API requests to backend
        if path.startswith("/api/") or path == "/health":
            return application(environ, start_response)
        
        # Serve static files from frontend/dist
        if path == "/":
            file_path = FRONTEND_DIST / "index.html"
            if file_path.exists():
                with open(file_path, 'r') as f:
                    response = Response(f.read(), mimetype='text/html')
                    return response(environ, start_response)
        
        # Check for assets (images, scripts, styles)
        if path.startswith("/assets/"):
            static_path = path[1:]  # Remove leading /
            file_path = FRONTEND_DIST / static_path
            if file_path.exists() and file_path.is_file():
                with open(file_path, 'rb') as f:
                    mimetype = 'application/octet-stream'
                    if static_path.endswith('.css'):
                        mimetype = 'text/css'
                    elif static_path.endswith('.js'):
                        mimetype = 'application/javascript'
                    elif static_path.endswith('.png'):
                        mimetype = 'image/png'
                    elif static_path.endswith('.jpg') or static_path.endswith('.jpeg'):
                        mimetype = 'image/jpeg'
                    elif static_path.endswith('.svg'):
                        mimetype = 'image/svg+xml'
                    
                    response = Response(wrap_file({}, f), mimetype=mimetype)
                    return response(environ, start_response)
        
        # Catch-all: serve index.html for React Router
        file_path = FRONTEND_DIST / "index.html"
        if file_path.exists():
            with open(file_path, 'r') as f:
                response = Response(f.read(), mimetype='text/html')
                return response(environ, start_response)
        
        # 404 Not Found
        response = Response(json.dumps({"error": "Not Found"}), status=404, mimetype='application/json')
        return response(environ, start_response)
    
    return integrated_application


def open_browser():
    """Open browser after a short delay"""
    time.sleep(2)
    url = f"http://{HOST}:{PORT}"
    print(f"\n🌐 Opening browser at: {url}")
    webbrowser.open(url)


def main():
    """Main application entry point"""
    print("\n" + "="*60)
    print("🍎 CALIBER - Food Classification & Health Chatbot")
    print("="*60)
    print(f"Backend: Pure Python WSGI (Werkzeug)")
    print(f"Frontend: React + Vite")
    print("="*60)
    
    is_production = os.getenv("RENDER") == "true" or os.getenv("PORT") is not None
    
    if is_production:
        print("\n🚀 Running in PRODUCTION mode (Render)")
        PORT_PROD = int(os.getenv("PORT", 10000))
        integrated_app = create_integrated_app()
        
        print(f"\n✅ Starting server on 0.0.0.0:{PORT_PROD}")
        run_simple("0.0.0.0", PORT_PROD, integrated_app, use_debugger=False, use_reloader=False)
    else:
        print("\n💻 Running in DEVELOPMENT mode")
        
        build_success = build_frontend()
        
        if build_success:
            integrated_app = create_integrated_app()
            
            browser_thread = Thread(target=open_browser, daemon=True)
            browser_thread.start()
            
            print(f"\n✅ Starting integrated server...")
            print(f"   🔗 Application: http://{HOST}:{PORT}")
            print(f"   🏥 Health Check: http://{HOST}:{PORT}/health")
            print(f"   💬 Chatbot: http://{HOST}:{PORT} (ChatWidget)")
            print("\n   Press Ctrl+C to stop the server")
            print("="*60 + "\n")
            
            try:
                run_simple(HOST, PORT, integrated_app, use_debugger=True, use_reloader=True)
            except KeyboardInterrupt:
                print("\n\n✅ Server stopped.")
        else:
            print("\n❌ Failed to build frontend. Start server with pre-built dist folder.")
            sys.exit(1)


if __name__ == "__main__":
    main()
                    port=PORT,
                    log_level="info"
                )
            except KeyboardInterrupt:
                print("\n\n👋 Shutting down gracefully...")
        else:
            print("\n❌ Failed to build frontend. Server not started.")
            print("   Please check the error messages above.")
            sys.exit(1)


if __name__ == "__main__":
    main()
