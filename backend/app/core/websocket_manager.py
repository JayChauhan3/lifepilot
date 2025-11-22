from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict
import structlog
import asyncio
import json

logger = structlog.get_logger()

class NotificationManager:
    def __init__(self):
        # Store active WebSocket connections by user_id
        self.active_connections: Dict[str, List[WebSocket]] = {}
        logger.info("NotificationManager initialized")
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        logger.info("WebSocket connected", user_id=user_id, total_connections=len(self.active_connections[user_id]))
    
    def disconnect(self, websocket: WebSocket, user_id: str):
        """Remove a WebSocket connection"""
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info("WebSocket disconnected", user_id=user_id)
    
    async def send_notification(self, user_id: str, notification: dict):
        """Send a notification to all connections for a user"""
        if user_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(notification)
                    logger.info("Notification sent", user_id=user_id, notification_id=notification.get("id"))
                except Exception as e:
                    logger.error("Failed to send notification", user_id=user_id, error=str(e))
                    disconnected.append(connection)
            
            # Clean up disconnected connections
            for conn in disconnected:
                self.disconnect(conn, user_id)
    
    async def broadcast_notification(self, notification: dict):
        """Send a notification to all connected users"""
        for user_id in list(self.active_connections.keys()):
            await self.send_notification(user_id, notification)

# Global notification manager instance
notification_manager = NotificationManager()
