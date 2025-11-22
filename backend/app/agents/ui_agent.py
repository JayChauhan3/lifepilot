# UI Agent
import structlog
from typing import List, Dict, Any
from ..schemas import AgentMessage
from ..core.a2a import A2AProtocol

logger = structlog.get_logger()

class UIAgent:
    def __init__(self):
        logger.info("UIAgent initialized")
    
    async def generate_dashboard(self, user_id: str, context: Dict[str, Any] = None) -> AgentMessage:
        """Generate structured dashboard data"""
        logger.info("Generating dashboard", user_id=user_id)
        
        # Mock dashboard data
        dashboard_data = {
            "layout": "grid",
            "widgets": [
                {
                    "id": "weather_widget",
                    "type": "weather",
                    "data": {"location": "San Francisco", "temp": 72, "condition": "Sunny"},
                    "position": {"x": 0, "y": 0, "w": 1, "h": 1}
                },
                {
                    "id": "tasks_widget",
                    "type": "task_list",
                    "data": {"tasks": ["Review PRs", "Team Sync", "Gym"]},
                    "position": {"x": 1, "y": 0, "w": 1, "h": 2}
                },
                {
                    "id": "plan_widget",
                    "type": "daily_plan",
                    "data": {"summary": "Focus on coding in the morning, meetings in afternoon"},
                    "position": {"x": 0, "y": 1, "w": 1, "h": 1}
                }
            ]
        }
        
        response = A2AProtocol.create_message(
            sender="ui",
            receiver="router",
            message_type="DASHBOARD_DATA",
            payload=dashboard_data
        )
        
        return response

    async def format_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format agent response into UI components"""
        logger.info("Formatting response for UI")
        
        # Transform raw data into UI-friendly format
        # This is a placeholder for more complex transformation logic
        return {
            "type": "chat_message",
            "content": response_data.get("content", ""),
            "components": [] # e.g. buttons, cards
        }
