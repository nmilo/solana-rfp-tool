"""
Vercel serverless function entry point for the FastAPI backend
"""

import sys
import os

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_path)

from app.main import app

# Export for Vercel
handler = app
