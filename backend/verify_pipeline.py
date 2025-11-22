import asyncio
import structlog
from dotenv import load_dotenv

# Load environment variables before importing app modules
load_dotenv()

from app.agents.router import RouterAgent
from app.core.orchestrator import orchestrator
from app.core.observability import observability

# Initialize observability
observability.initialize()

logger = structlog.get_logger()

async def verify_pipeline():
    print("\n🚀 Starting Whole Pipeline Verification 🚀\n")
    
    # Initialize Router
    router = RouterAgent()
    
    # 1. Test "Plan my day" (Planner -> Orchestrator)
    print("--- 1. Testing Planning Pipeline ---")
    plan_request = "Plan my day. I need to code in the morning, have a team meeting at 2pm, and go grocery shopping for dinner."
    response = await router.process_message("user_verify", plan_request)
    print(f"Response: {response['response'][:100]}...")
    assert "plan" in response["response"].lower() or "schedule" in response["response"].lower()
    
    # 2. Test "Track my tasks" (Executor/Memory)
    print("\n--- 2. Testing Task Execution ---")
    task_request = "Schedule a meeting with the team for tomorrow at 10am"
    workflow_id = await orchestrator.create_workflow("user_verify", task_request)
    print(f"Created Workflow: {workflow_id}")
    await asyncio.sleep(5) # Wait for execution
    status = orchestrator.get_workflow_status(workflow_id)
    print(f"Workflow Status: {status['status']}")
    if status['status'] != 'completed':
        workflow = orchestrator.workflows.get(workflow_id)
        if workflow:
            for step in workflow.steps:
                print(f"Step: {step.name}, Status: {step.status}, Error: {step.error}")
    assert status['status'] == 'completed'
    
    # 3. Test "Recommend meals/Check weather" (Knowledge)
    print("\n--- 3. Testing Knowledge Search ---")
    search_request = "Find a recipe for pasta carbonara"
    response = await router.process_message("user_verify", search_request)
    print(f"Response: {response['response'][:100]}...")
    assert "pasta" in response["response"].lower() or "recipe" in response["response"].lower()
    
    # 4. Test "Send alerts" (Notification)
    print("\n--- 4. Testing Notifications ---")
    alert_request = "Send an alert to check the oven in 10 minutes"
    workflow_id = await orchestrator.create_workflow("user_verify", alert_request)
    print(f"Created Alert Workflow: {workflow_id}")
    await asyncio.sleep(2)
    status = orchestrator.get_workflow_status(workflow_id)
    print(f"Workflow Status: {status['status']}")
    if status['status'] != 'completed':
        workflow = orchestrator.workflows.get(workflow_id)
        if workflow:
            for step in workflow.steps:
                print(f"Step: {step.name}, Status: {step.status}, Error: {step.error}")
    
    # 5. Test "Reflect on habits" (Analyzer)
    print("\n--- 5. Testing Analysis ---")
    analysis_request = "Analyze my productivity this week"
    workflow_id = await orchestrator.create_workflow("user_verify", analysis_request)
    print(f"Created Analysis Workflow: {workflow_id}")
    await asyncio.sleep(3)
    status = orchestrator.get_workflow_status(workflow_id)
    print(f"Workflow Status: {status['status']}")
    if status['status'] != 'completed':
        workflow = orchestrator.workflows.get(workflow_id)
        if workflow:
            for step in workflow.steps:
                print(f"Step: {step.name}, Status: {step.status}, Error: {step.error}")
    assert status['status'] == 'completed'

    # 6. Test "Show Dashboard" (UI)
    print("\n--- 6. Testing UI ---")
    ui_request = "Show my dashboard"
    response = await router.process_message("user_verify", ui_request)
    print(f"Response Text: {response['response']}")
    print(f"Response Data: {response.get('data', {}).keys()}")
    assert "dashboard" in response["response"].lower()
    assert "widgets" in response["data"]

    print("\n✅ Whole Pipeline Verification Completed Successfully! 🚀")

if __name__ == "__main__":
    asyncio.run(verify_pipeline())
