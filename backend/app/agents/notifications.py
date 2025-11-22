# Notification Agent
import structlog
from typing import List, Dict, Any
from datetime import datetime
from ..core.a2a import A2AProtocol
from ..schemas import AgentMessage

logger = structlog.get_logger()

class NotificationAgent:
    def __init__(self):
        logger.info("NotificationAgent initialized")
        self.pending_alerts: List[Dict[str, Any]] = []
    
    async def send_alert(self, user_id: str, message: str, priority: str = "normal") -> AgentMessage:
        """Send a notification alert"""
        logger.info("Sending alert", user_id=user_id, priority=priority)
        
        alert = {
            "id": f"alert_{int(datetime.now().timestamp())}",
            "user_id": user_id,
            "message": message,
            "priority": priority,
            "created_at": datetime.now().isoformat(),
            "status": "sent",
            "read": False
        }
        
        # Store in memory
        self.pending_alerts.append(alert)
        
        # Send via WebSocket if available
        try:
            from ..core.websocket_manager import notification_manager
            await notification_manager.send_notification(user_id, {
                "type": "notification",
                "data": alert
            })
            logger.info("WebSocket notification sent", alert_id=alert["id"])
        except Exception as e:
            logger.warning("Failed to send WebSocket notification", error=str(e))
        
        response = A2AProtocol.create_message(
            sender="notifications",
            receiver="router",
            message_type="ALERT_SENT",
            payload=alert
        )
        
        logger.info("Alert sent", alert_id=alert["id"])
        return response

    async def get_pending_alerts(self, user_id: str) -> List[Dict[str, Any]]:
        """Get pending alerts for a user"""
        logger.info("Getting pending alerts", user_id=user_id)
        
        # Filter alerts for user
        user_alerts = [a for a in self.pending_alerts if a["user_id"] == user_id]
        
        # Clear retrieved alerts (assuming they are consumed)
        self.pending_alerts = [a for a in self.pending_alerts if a["user_id"] != user_id]
        
        return user_alerts

    async def process_task(self, task: str, context: Dict[str, Any] = None) -> AgentMessage:
        """Process a generic notification task"""
        # Extract user_id from context or use default
        user_id = context.get("user_id", "default_user") if context else "default_user"
        
        # Send alert with task description
        await self.send_alert(user_id, task, "medium")
        
        return AgentMessage(
            sender="notifications",
            receiver="orchestrator",
            type="NOTIFICATION_SENT",
            payload={
                "task": task,
                "status": "completed",
                "result": f"Notification sent for: {task}"
            }
        )
