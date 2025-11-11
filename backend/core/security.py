"""
Security Module
CORS and security configurations
"""

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

def setup_cors(app: FastAPI, origins: list = None):
    """Setup CORS middleware"""
    if origins is None:
        origins = [
            "http://localhost:8501",
            "http://127.0.0.1:8501",
            "http://localhost:8080",
            "http://127.0.0.1:8080",
            "https://*.render.com"  # Render deployment
        ]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins for development
        allow_credentials=True,
        allow_methods=["*"],  # Allow all HTTP methods including OPTIONS
        allow_headers=["*"],  # Allow all headers
        expose_headers=["*"],  # Expose all headers
    )

