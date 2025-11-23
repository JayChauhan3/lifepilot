import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.agents.planner import PlannerAgent
from app.agents.executor import ExecutorAgent
from datetime import datetime

@pytest.mark.unit
class TestPlannerAgentUnit:
    """Unit tests for PlannerAgent with mocked dependencies"""
    
    @pytest.fixture
    def mock_llm_service(self, mocker):
        """Mock LLM service"""
        mock = mocker.MagicMock()
        mock.generate_plan = MagicMock(return_value={
            "title": "Test Plan",
            "description": "A test plan",
            "steps": [
                {"action": "Step 1", "details": "First step"},
                {"action": "Step 2", "details": "Second step"}
            ],
            "priority": "high",
            "timeline": "1 hour"
        })
        return mock
    
    @pytest.fixture
    def mock_memory_bank(self, mocker):
        """Mock MemoryBank"""
        mock = mocker.MagicMock()
        mock.retrieve_relevant_context = MagicMock(return_value=[])
        mock.store_memory = MagicMock(return_value=True)
        return mock
    
    @pytest.fixture
    def planner_agent(self, mocker, mock_llm_service, mock_memory_bank):
        """PlannerAgent with mocked dependencies"""
        agent = PlannerAgent()
        mocker.patch.object(agent, 'llm_service', mock_llm_service)
        mocker.patch.object(agent, 'memory_bank', mock_memory_bank)
        return agent
    
    @pytest.mark.asyncio
    async def test_create_plan_unit(self, planner_agent, mock_llm_service, mock_memory_bank):
        """Test plan creation without real LLM or database"""
        user_message = "Plan my day"
        user_id = "test_user"
        
        # Execute
        result = await planner_agent.create_plan(user_message, user_id)
        
        # Assert
        assert result.sender == "planner"
        assert result.type == "PLAN_RESPONSE"
        assert "steps" in result.payload
        assert len(result.payload["steps"]) > 0
        
        # Verify mocks were called
        mock_memory_bank.retrieve_relevant_context.assert_called_once()
        mock_llm_service.generate_plan.assert_called_once()
        mock_memory_bank.store_memory.assert_called_once()

@pytest.mark.unit
class TestExecutorAgentUnit:
    """Unit tests for ExecutorAgent with mocked dependencies"""
    
    @pytest.fixture
    def mock_python_tool(self, mocker):
        """Mock PythonExecutionTool"""
        mock = mocker.MagicMock()
        mock.execute = MagicMock(return_value={
            "success": True,
            "result": 42,
            "stdout": "Calculation result: 42",
            "error": None
        })
        return mock
    
    @pytest.fixture
    def mock_calendar_tool(self, mocker):
        """Mock CalendarTool"""
        mock = mocker.MagicMock()
        mock.create_event = MagicMock(return_value={
            "id": "event123",
            "title": "Test Event"
        })
        return mock
    
    @pytest.fixture
    def executor_agent(self, mocker, mock_python_tool, mock_calendar_tool):
        """ExecutorAgent with mocked dependencies"""
        agent = ExecutorAgent()
        mocker.patch.object(agent, 'python_tool', mock_python_tool)
        mocker.patch.object(agent, 'calendar_tool', mock_calendar_tool)
        return agent
    
    @pytest.mark.asyncio
    async def test_execute_calculation_task_unit(self, executor_agent, mock_python_tool):
        """Test executing calculation task without real Python execution"""
        task = "calculate 2 + 2"
        
        # Execute
        result = await executor_agent.execute_task(task)
        
        # Assert
        assert result.sender == "executor"
        assert result.type == "EXECUTION_RESPONSE"
        assert "result" in result.payload
        
        # Verify Python tool was called
        mock_python_tool.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_scheduling_task_unit(self, executor_agent, mock_calendar_tool):
        """Test executing scheduling task without real calendar"""
        task = "schedule a meeting tomorrow"
        
        # Execute
        result = await executor_agent.execute_task(task)
        
        # Assert
        assert result.sender == "executor"
        assert "scheduled" in result.payload["result"].lower()
        
        # Verify calendar tool was called
        mock_calendar_tool.create_event.assert_called_once()
