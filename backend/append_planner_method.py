import os

planner_path = "/Users/jaychauhan/Documents/GitHub/lifepilot/backend/app/agents/planner.py"

method_code = """

    async def process_task(self, task: str, context: Dict[str, Any] = None) -> AgentMessage:
        \"\"\"Process a generic planning task\"\"\"
        logger.info("Processing planning task", task=task)
        
        # Use LLM to perform the planning task
        try:
            response = self.llm_service.generate_text(
                f"Perform the following planning task: {task}. Provide the result.",
                max_tokens=500
            )
            result = response
            status = "completed"
        except Exception as e:
            logger.error("Failed to process planning task", error=str(e))
            result = f"Failed to process task: {str(e)}"
            status = "failed"
            
        return AgentMessage(
            sender="planner",
            receiver="orchestrator",
            type="PLANNING_RESULT",
            payload={
                "task": task,
                "result": result,
                "status": status,
                "timestamp": datetime.now().isoformat()
            }
        )
"""

with open(planner_path, "a") as f:
    f.write(method_code)

print("Successfully appended process_task to PlannerAgent")
