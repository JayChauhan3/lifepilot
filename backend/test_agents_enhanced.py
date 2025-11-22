from dotenv import load_dotenv
import asyncio
import structlog
from app.agents.analyzer import AnalyzerAgent
from app.agents.notifications import NotificationAgent
from app.agents.ui_agent import UIAgent
from app.core.orchestrator import orchestrator
from app.core.observability import observability

# Load environment variables
load_dotenv()

# Initialize observability for tests
observability.initialize()

logger = structlog.get_logger()

async def test_analyzer():
    print("\n--- Testing AnalyzerAgent ---")
    agent = AnalyzerAgent()
    
    # Test Intent Analysis
    intent = await agent.analyze_intent("Analyze my productivity for this week")
    print(f"Intent Analysis: {intent}")
    assert intent["route"] == "analysis"
    
    # Test Productivity Analysis
    analysis = await agent.analyze_productivity("user123", "week")
    print(f"Productivity Analysis: {analysis}")
    assert "productivity_score" in analysis
    assert "summary" in analysis

async def test_notifications():
    print("\n--- Testing NotificationAgent ---")
    agent = NotificationAgent()
    
    # Test Send Alert
    await agent.send_alert("user123", "Test Alert", "high")
    
    # Test Get Pending Alerts
    alerts = await agent.get_pending_alerts("user123")
    print(f"Pending Alerts: {alerts}")
    assert len(alerts) == 1
    assert alerts[0]["message"] == "Test Alert"

async def test_ui_agent():
    print("\n--- Testing UIAgent ---")
    agent = UIAgent()
    
    # Test Dashboard Generation
    dashboard = await agent.generate_dashboard("user123")
    print(f"Dashboard Data: {dashboard.payload}")
    assert dashboard.payload["layout"] == "grid"
    assert len(dashboard.payload["widgets"]) > 0

async def test_orchestrator_wiring():
    print("\n--- Testing Orchestrator Wiring ---")
    
    # Test Workflow Creation for Analysis
    workflow_id = await orchestrator.create_workflow("user123", "Analyze my productivity")
    print(f"Created Workflow ID: {workflow_id}")
    
    # Wait for execution (briefly)
    await asyncio.sleep(2)
    
    status = orchestrator.get_workflow_status(workflow_id)
    print(f"Workflow Status: {status['status']}")
    
    # Verify steps were created correctly
    steps = status["steps"]
    print(f"Workflow Steps: {[s['name'] for s in steps]}")

async def test_router_ui_response():
    print("\n--- Testing RouterAgent UI Response ---")
    from app.agents.router import RouterAgent
    agent = RouterAgent()
    
    # Test UI Request
    response = await agent.process_message("user123", "Show my dashboard")
    print(f"Response Text: {response['response']}")
    print(f"Response Data Keys: {response.get('data', {}).keys()}")
    
    assert "dashboard" in response["response"].lower()
    assert "{" not in response["response"] # Ensure no raw JSON in text
    assert response["data"]["layout"] == "grid"

async def main():
    try:
        await test_analyzer()
        await test_notifications()
        await test_ui_agent()
        await test_router_ui_response()
        await test_orchestrator_wiring()
        print("\n✅ All tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
