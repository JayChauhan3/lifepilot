#!/usr/bin/env python3
"""
Startup script for LifePilot backend
"""

import uvicorn
import sys
import os

# Add compatibility for Python 3.9 missing packages_distributions
if sys.version_info < (3, 10):
    import importlib.metadata
    if not hasattr(importlib.metadata, 'packages_distributions'):
        def packages_distributions():
            """Compatibility shim for Python 3.9"""
            return {}
        importlib.metadata.packages_distributions = packages_distributions

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

if __name__ == "__main__":
    print("🚀 Starting LifePilot Backend...")
    print("📡 API will be available at: http://localhost:8000")
    print("📖 API docs at: http://localhost:8000/docs")
    print("🏥 Health check at: http://localhost:8000/health")
    print("\n🔌 Available endpoints:")
    print("   POST /api/chat - Chat with LifePilot AI")
    print("   GET  / - Welcome message")
    print("   GET  /health - Health check")
    print("\n⚡ Starting server...")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
