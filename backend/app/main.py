# FastAPI startup
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
load_dotenv()

import structlog
from app.api.chat import router as chat_router
from app.core.orchestrator import orchestrator
from app.core.websocket_manager import notification_manager

logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("Starting LifePilot API application")
    await orchestrator.start()
    
    yield
    
    # Shutdown
    logger.info("Shutting down LifePilot API application")
    await orchestrator.stop()

# Create FastAPI app
app = FastAPI(
    title="LifePilot API",
    description="AI-powered personal assistant API",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router, prefix="/api")

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "LifePilot API is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "lifepilot-api"}

@app.websocket("/ws/notifications/{user_id}")
async def websocket_notifications(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time notifications"""
    await notification_manager.connect(websocket, user_id)
    try:
        while True:
            # Keep connection alive and listen for messages
            data = await websocket.receive_text()
            logger.debug("WebSocket message received", user_id=user_id, data=data)
    except WebSocketDisconnect:
        notification_manager.disconnect(websocket, user_id)
        logger.info("WebSocket disconnected", user_id=user_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
