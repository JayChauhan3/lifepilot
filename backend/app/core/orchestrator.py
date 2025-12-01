"""
Multi-Agent Orchestrator
Coordinates agent interactions and manages workflow execution
"""

import structlog
import asyncio
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import uuid
from datetime import datetime, timedelta

from app.core.a2a import A2AProtocol
from app.core.longrunner import long_runner, TaskStatus, update_progress
from app.core.observability import trace_function, trace_context, structured_logger
from app.agents.planner import PlannerAgent
from app.agents.executor import ExecutorAgent
from app.agents.router import RouterAgent
from app.agents.analyzer import AnalyzerAgent
from app.agents.knowledge import KnowledgeAgent
from app.agents.notifications import NotificationAgent
from app.agents.ui_agent import UIAgent
from app.agents.routine_agent import routine_agent

logger = structlog.get_logger()

class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"

@dataclass
class WorkflowStep:
    """Represents a step in a workflow"""
    step_id: str
    name: str
    agent_type: str
    action: str
    parameters: Dict[str, Any]
    dependencies: List[str] = None
    timeout_seconds: int = 300
    retry_count: int = 0
    max_retries: int = 3
    status: WorkflowStatus = WorkflowStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

@dataclass
class Workflow:
    """Represents a complete workflow"""
    workflow_id: str
    name: str
    description: str
    user_id: str
    steps: List[WorkflowStep]
    status: WorkflowStatus = WorkflowStatus.PENDING
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    context: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.context is None:
            self.context = {}

class MultiAgentOrchestrator:
    """
    Orchestrates multi-agent workflows and interactions.
    
    ARCHITECTURE NOTE:
    This class implements the "Hub-and-Spoke" pattern where the Orchestrator acts as the central hub,
    managing state and coordinating specialized agents (spokes).
    
    Key Responsibilities:
    1. Workflow Management: Decomposing requests into execution steps.
    2. State Machine: Tracking the lifecycle of workflows (PENDING -> RUNNING -> COMPLETED).
    3. A2A Communication: Facilitating standardized message passing between agents.
    """
    
    def __init__(self):
        self.a2a_protocol = A2AProtocol()
        self.workflows: Dict[str, Workflow] = {}
        self.running_workflows: Dict[str, asyncio.Task] = {}
        
        # Initialize agents
        self.agents = {
            "planner": PlannerAgent(),
            "executor": ExecutorAgent(),
            "router": RouterAgent(),
            "analyzer": AnalyzerAgent(),
            "knowledge": KnowledgeAgent(),
            "ui": UIAgent(),
            "routine": routine_agent
        }
        
        # Start routine agent scheduler
        # Moved to start() method to avoid side effects during import
        # asyncio.create_task(routine_agent.start_scheduler())
        
        logger.info("Multi-agent orchestrator initialized", agents=list(self.agents.keys()))
    
    async def start(self):
        """Start the orchestrator and background tasks"""
        logger.info("Starting orchestrator background tasks")
        # Start routine agent scheduler
        # We use create_task to run it in background without blocking
        self._scheduler_task = asyncio.create_task(routine_agent.start_scheduler())
        
    async def stop(self):
        """Stop the orchestrator and background tasks"""
        logger.info("Stopping orchestrator background tasks")
        await routine_agent.stop_scheduler()
    
    @trace_function("orchestrator.create_workflow")
    async def create_workflow(self, user_id: str, request: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Create a new workflow from user request"""
        workflow_id = str(uuid.uuid4())
        
        try:
            # Analyze user intent
            analyzer_result = await self._call_agent(
                "analyzer", 
                "analyze_intent", 
                {"message": request, "context": context}
            )
            
            # Create plan
            planner_result = await self._call_agent(
                "planner",
                "create_plan",
                {"user_message": request, "context": context}
            )
            
            # Convert plan to workflow steps
            # Handle AgentMessage response
            if hasattr(planner_result, 'payload'):
                plan_data = planner_result.payload
            else:
                plan_data = planner_result.get("plan", planner_result)
                
            steps = self._plan_to_steps(plan_data)
            
            # Create workflow
            workflow = Workflow(
                workflow_id=workflow_id,
                name=f"Workflow for: {request[:50]}...",
                description=request,
                user_id=user_id,
                steps=steps,
                context=context or {}
            )
            
            self.workflows[workflow_id] = workflow
            
            logger.info("Workflow created", workflow_id=workflow_id, user_id=user_id, steps=len(steps))
            
            # Start workflow execution
            task = asyncio.create_task(self._execute_workflow(workflow_id))
            self.running_workflows[workflow_id] = task
            
            return workflow_id
            
        except Exception as e:
            logger.error("Failed to create workflow", error=str(e), user_id=user_id)
            raise
    
    @trace_function("orchestrator.execute_workflow")
    async def _execute_workflow(self, workflow_id: str):
        """
        Execute a workflow.
        
        IMPLEMENTATION DETAIL:
        This method implements a non-blocking execution loop that:
        1. Identifies ready steps (dependencies met).
        2. Executes independent steps in parallel using asyncio.gather().
        3. Updates workflow state and handles failures/deadlocks.
        """
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            logger.error("Workflow not found", workflow_id=workflow_id)
            return
        
        try:
            workflow.status = WorkflowStatus.RUNNING
            workflow.started_at = datetime.now()
            
            structured_logger.log_agent_interaction(
                "orchestrator",
                "workflow_started",
                workflow.user_id
            )
            
            # Execute steps in dependency order
            completed_steps = set()
            
            while len(completed_steps) < len(workflow.steps):
                # Find steps ready to execute
                ready_steps = [
                    step for step in workflow.steps
                    if step.status == WorkflowStatus.PENDING and
                    (not step.dependencies or all(dep in completed_steps for dep in step.dependencies))
                ]
                
                if not ready_steps:
                    # Check if any steps failed
                    failed_steps = [s for s in workflow.steps if s.status == WorkflowStatus.FAILED]
                    if failed_steps:
                        workflow.status = WorkflowStatus.FAILED
                        logger.error("Workflow failed due to failed steps", 
                                   workflow_id=workflow_id, failed_steps=[s.step_id for s in failed_steps])
                        break
                    
                    # No ready steps and no failures - likely a deadlock
                    logger.error("Workflow deadlock detected", workflow_id=workflow_id)
                    workflow.status = WorkflowStatus.FAILED
                    break
                
                # Execute ready steps in parallel
                await asyncio.gather(
                    *[self._execute_step(workflow_id, step) for step in ready_steps],
                    return_exceptions=True
                )
                
                # Update completed steps
                newly_completed = {s.step_id for s in workflow.steps if s.status == WorkflowStatus.COMPLETED}
                completed_steps.update(newly_completed)
            
            # Check final status
            if all(s.status == WorkflowStatus.COMPLETED for s in workflow.steps):
                workflow.status = WorkflowStatus.COMPLETED
                workflow.completed_at = datetime.now()
                
                structured_logger.log_agent_interaction(
                    "orchestrator",
                    "workflow_completed",
                    workflow.user_id
                )
            
        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            workflow.completed_at = datetime.now()
            logger.error("Workflow execution failed", workflow_id=workflow_id, error=str(e))
            
        finally:
            # Clean up running task
            if workflow_id in self.running_workflows:
                del self.running_workflows[workflow_id]
    
    @trace_function("orchestrator.execute_step")
    async def _execute_step(self, workflow_id: str, step: WorkflowStep):
        """Execute a single workflow step"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return
        
        step.status = WorkflowStatus.RUNNING
        step.started_at = datetime.now()
        
        try:
            with trace_context(f"workflow_step_{step.step_id}", {
                "workflow_id": workflow_id,
                "step_id": step.step_id,
                "agent": step.agent_type,
                "action": step.action
            }):
                
                logger.info("Executing workflow step", 
                           workflow_id=workflow_id, 
                           step_id=step.step_id,
                           agent=step.agent_type,
                           action=step.action)
                
                # Call agent with timeout
                result = await asyncio.wait_for(
                    self._call_agent(step.agent_type, step.action, step.parameters),
                    timeout=step.timeout_seconds
                )
                
                step.status = WorkflowStatus.COMPLETED
                step.result = result
                step.completed_at = datetime.now()
                
                logger.info("Workflow step completed", 
                           workflow_id=workflow_id, 
                           step_id=step.step_id)
                
        except asyncio.TimeoutError:
            step.status = WorkflowStatus.FAILED
            step.error = "Step execution timed out"
            logger.error("Workflow step timed out", 
                        workflow_id=workflow_id, 
                        step_id=step.step_id)
            
        except Exception as e:
            step.status = WorkflowStatus.FAILED
            step.error = str(e)
            logger.error("Workflow step failed", 
                        workflow_id=workflow_id, 
                        step_id=step.step_id,
                        error=str(e))
            
            # Retry logic
            if step.retry_count < step.max_retries:
                step.retry_count += 1
                step.status = WorkflowStatus.PENDING
                logger.info("Retrying workflow step", 
                           workflow_id=workflow_id, 
                           step_id=step.step_id,
                           attempt=step.retry_count)
    
    @trace_function("orchestrator.call_agent")
    async def _call_agent(self, agent_type: str, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Call an agent with A2A messaging"""
        agent = self.agents.get(agent_type)
        if not agent:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        # Create A2A message
        message = self.a2a_protocol.create_message(
            sender="orchestrator",
            receiver=f"{agent_type}_agent",
            message_type=action,
            payload=parameters
        )
        
        # Process message through agent
        if hasattr(agent, 'process_message'):
            # RouterAgent.process_message expects (user_id, message: str)
            if agent_type == "router":
                user_id = parameters.get("user_id", "default_user")
                # For RouterAgent, the 'message' is the action description
                result = await agent.process_message(user_id, action)
            else:
                result = await agent.process_message(message)
        elif hasattr(agent, action):
            method = getattr(agent, action)
            if asyncio.iscoroutinefunction(method):
                result = await method(**parameters)
            else:
                result = method(**parameters)
        elif hasattr(agent, 'process_task'):
            # Fallback for generic tasks
            # Pass the action description as the task
            task_desc = action
            if parameters:
                task_desc += f" with details: {parameters}"
            result = await agent.process_task(task_desc)
        else:
            raise ValueError(f"Agent {agent_type} doesn't support action {action}")
        
        structured_logger.log_agent_interaction(agent_type, action)
        
        return result
    
    def _plan_to_steps(self, plan: Dict[str, Any]) -> List[WorkflowStep]:
        """Convert planner result to workflow steps"""
        steps = []
        plan_steps = plan.get("steps", [])
        
        for i, plan_step in enumerate(plan_steps):
            if isinstance(plan_step, str):
                action = plan_step
                details = {}
            elif hasattr(plan_step, 'payload'): # Handle AgentMessage
                action = plan_step.payload.get("action", "Unknown Action")
                details = plan_step.payload.get("details", {})
            else:
                action = plan_step.get("action", str(plan_step))
                details = plan_step.get("details", {})
                
            # Ensure action is a string for agent determination
            action_str = action if isinstance(action, str) else str(action)
            
            step = WorkflowStep(
                step_id=f"step_{i+1}",
                name=action_str,
                agent_type=self._determine_agent_for_action(action_str),
                action=action_str,
                parameters=details,
                dependencies=[f"step_{i}"] if i > 0 else []
            )
            steps.append(step)
        
        return steps
    
    def _determine_agent_for_action(self, action: str) -> str:
        """Determine which agent should handle an action"""
        # Ensure action is a string
        if hasattr(action, 'payload'):
            action = action.payload.get("action", str(action))
        elif not isinstance(action, str):
            action = str(action)
            
        action_lower = action.lower()
        
        if any(keyword in action_lower for keyword in ["plan", "organize"]):
            return "planner"
        elif any(keyword in action_lower for keyword in ["execute", "perform", "do", "complete", "schedule", "availability"]):
            return "executor"
        elif any(keyword in action_lower for keyword in ["search", "find", "lookup", "research"]):
            return "knowledge"
        elif any(keyword in action_lower for keyword in ["analyze", "understand", "interpret", "summary"]):
            return "analyzer"
        elif any(keyword in action_lower for keyword in ["show", "display", "render", "dashboard"]):
            return "ui"
        else:
            return "router"  # Default to router
    
    async def pause_workflow(self, workflow_id: str) -> bool:
        """Pause a running workflow"""
        workflow = self.workflows.get(workflow_id)
        if not workflow or workflow.status != WorkflowStatus.RUNNING:
            return False
        
        workflow.status = WorkflowStatus.PAUSED
        
        # Cancel the running task
        if workflow_id in self.running_workflows:
            task = self.running_workflows[workflow_id]
            task.cancel()
            del self.running_workflows[workflow_id]
        
        logger.info("Workflow paused", workflow_id=workflow_id)
        return True
    
    async def resume_workflow(self, workflow_id: str) -> bool:
        """Resume a paused workflow"""
        workflow = self.workflows.get(workflow_id)
        if not workflow or workflow.status != WorkflowStatus.PAUSED:
            return False
        
        # Restart workflow execution
        task = asyncio.create_task(self._execute_workflow(workflow_id))
        self.running_workflows[workflow_id] = task
        
        logger.info("Workflow resumed", workflow_id=workflow_id)
        return True
    
    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a workflow"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return False
        
        workflow.status = WorkflowStatus.CANCELLED
        
        # Cancel the running task
        if workflow_id in self.running_workflows:
            task = self.running_workflows[workflow_id]
            task.cancel()
            del self.running_workflows[workflow_id]
        
        logger.info("Workflow cancelled", workflow_id=workflow_id)
        return True
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow status and details"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return None
        
        return {
            "workflow_id": workflow.workflow_id,
            "name": workflow.name,
            "description": workflow.description,
            "user_id": workflow.user_id,
            "status": workflow.status.value,
            "created_at": workflow.created_at.isoformat(),
            "started_at": workflow.started_at.isoformat() if workflow.started_at else None,
            "completed_at": workflow.completed_at.isoformat() if workflow.completed_at else None,
            "steps": [
                {
                    "step_id": step.step_id,
                    "name": step.name,
                    "agent_type": step.agent_type,
                    "action": step.action,
                    "status": step.status.value,
                    "started_at": step.started_at.isoformat() if step.started_at else None,
                    "completed_at": step.completed_at.isoformat() if step.completed_at else None,
                    "error": step.error,
                    "retry_count": step.retry_count
                }
                for step in workflow.steps
            ]
        }
    
    def list_workflows(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List workflows for a user or all workflows"""
        workflows = []
        
        for workflow in self.workflows.values():
            if user_id and workflow.user_id != user_id:
                continue
            
            workflows.append({
                "workflow_id": workflow.workflow_id,
                "name": workflow.name,
                "status": workflow.status.value,
                "created_at": workflow.created_at.isoformat(),
                "step_count": len(workflow.steps),
                "completed_steps": len([s for s in workflow.steps if s.status == WorkflowStatus.COMPLETED])
            })
        
        return workflows
    
    async def cleanup_completed_workflows(self, max_age_hours: int = 24):
        """Clean up old completed workflows"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        to_remove = []
        for workflow_id, workflow in self.workflows.items():
            if (workflow.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED] and
                workflow.completed_at and workflow.completed_at < cutoff_time):
                to_remove.append(workflow_id)
        
        for workflow_id in to_remove:
            del self.workflows[workflow_id]
            logger.info("Cleaned up old workflow", workflow_id=workflow_id)
        
        return len(to_remove)

# Global orchestrator instance
orchestrator = MultiAgentOrchestrator()
