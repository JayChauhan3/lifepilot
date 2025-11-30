# FastAPI startup
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
load_dotenv()

import structlog
from app.api.chat import router as chat_router
from app.api.tasks import router as tasks_router
from app.api.routines import router as routines_router
from app.api.users import router as users_router
from app.api.auth import router as auth_router
from app.api.history import router as history_router
from app.core.orchestrator import orchestrator
from app.core.websocket_manager import notification_manager
from app.core.database import connect_to_mongo, close_mongo_connection, get_connection_status
from app.tasks.scheduler import start_scheduler, stop_scheduler
from app.middleware import (
    global_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    logging_middleware,
    limiter,
)
from app.config import settings
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("Starting LifePilot API application")
    await connect_to_mongo()
    start_scheduler()  # Start task scheduler
    await orchestrator.start()
    
    yield
    
    # Shutdown
    logger.info("Shutting down LifePilot API application")
    await orchestrator.stop()
    stop_scheduler()  # Stop task scheduler
    await close_mongo_connection()

# Create FastAPI app
app = FastAPI(
    title="LifePilot API",
    description="AI-powered personal assistant API",
    version="1.0.0",
    lifespan=lifespan
)

# Add rate limiter
app.state.limiter = limiter

# Configure CORS with specific origins
allowed_origins = settings.CORS_ORIGINS.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add session middleware for OAuth
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.JWT_SECRET_KEY  # Use JWT secret for session
)

# Add custom middleware
app.middleware("http")(logging_middleware)

# Add exception handlers
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(tasks_router, prefix="/api")
app.include_router(routines_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(history_router, prefix="/api")

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "LifePilot API is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint with database status"""
    db_status = get_connection_status()
    return {
        "status": "healthy",
        "service": "lifepilot-api",
        "database": db_status
    }

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
    
