"""
Vercel Python API Handler
Wraps FastAPI app for Vercel serverless deployment
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app

handler = app  # Vercel Python uses ASGI directly
