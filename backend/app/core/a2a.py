# A2A helpers
import structlog
from app.schemas import AgentMessage
from typing import Dict, Any, Optional
import json

logger = structlog.get_logger()

class A2AProtocol:
    """Agent-to-Agent communication protocol"""
    
    @staticmethod
    def create_message(sender: str, receiver: str, message_type: str, payload: Dict[str, Any]) -> AgentMessage:
        """Create a standardized agent message"""
        logger.info("Creating A2A message", sender=sender, receiver=receiver, type=message_type)
        return AgentMessage(
            sender=sender,
            receiver=receiver,
            type=message_type,
            payload=payload
        )
    
    @staticmethod
    def serialize_message(message: AgentMessage) -> str:
        """Serialize message to JSON"""
        return message.json()
    
    @staticmethod
    def deserialize_message(json_str: str) -> AgentMessage:
        """Deserialize message from JSON"""
        data = json.loads(json_str)
        return AgentMessage(**data)
    
    @staticmethod
    def validate_message(message: AgentMessage) -> bool:
        """Validate message structure"""
        required_fields = ["sender", "receiver", "type", "payload"]
        for field in required_fields:
            if not hasattr(message, field) or getattr(message, field) is None:
                logger.error("Message validation failed", missing_field=field)
                return False
        return True