# Vercel serverless function for FastAPI
import sys
import os

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_path)

# Set environment variables
os.environ.setdefault('PYTHONPATH', backend_path)

# Import the FastAPI app
from app.main import app

# Export the app for Vercel
# Vercel will automatically handle FastAPI apps
handler = app

# For local testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
