"""
Test script to send a notification via WebSocket
"""
import asyncio
import sys
sys.path.insert(0, '/Users/jaychauhan/Documents/GitHub/lifepilot/backend')

from app.agents.notifications import NotificationAgent

async def test_notification():
    """Send a test notification"""
    agent = NotificationAgent()
    
    # Send a high priority notification
    await agent.send_alert(
        user_id="user_1763661039644_5z0a56vfq",  # Replace with actual user_id from logs
        message="🎉 WebSocket notifications are working! This is a test notification.",
        priority="high"
    )
    
    print("Test notification sent!")
    
    # Wait a bit
    await asyncio.sleep(2)
    
    # Send a medium priority notification
    await agent.send_alert(
        user_id="user_1763661039644_5z0a56vfq",
        message="Meeting reminder: Team standup in 15 minutes",
        priority="medium"
    )
    
    print("Second notification sent!")

if __name__ == "__main__":
    asyncio.run(test_notification())
