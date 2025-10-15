#!/usr/bin/env python3
"""
Run the FastAPI app locally for testing
"""
import sys
import os

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'webapp/backend'))

# Set environment variables for local testing
os.environ['DATABASE_URL'] = 'sqlite:///./test.db'
os.environ['SECRET_KEY'] = 'local-test-secret-key-change-in-production'
os.environ['ENVIRONMENT'] = 'local'

if __name__ == "__main__":
    import uvicorn
    from app.main import app
    
    print("🚀 Starting GRC AI Governance Framework (Local Mode)")
    print("-" * 50)
    print("📍 Server: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("📊 Dashboard: http://localhost:8000/")
    print("-" * 50)
    print("Press Ctrl+C to stop the server")
    print("")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
