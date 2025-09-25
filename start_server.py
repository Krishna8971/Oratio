#!/usr/bin/env python3
"""
Start server script with environment configuration
"""

import os
import uvicorn

# Load environment variables
try:
    import environment
    print("✅ Environment variables loaded from environment.py")
except ImportError:
    print("⚠️ environment.py not found, using system environment variables")

if __name__ == "__main__":
    print("Starting Oratio server with Gemini API...")
    print(f"GEMINI_API_KEY set: {bool(os.environ.get('GEMINI_API_KEY'))}")
    print(f"GEMINI_MODEL: {os.environ.get('GEMINI_MODEL', 'Not set')}")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
