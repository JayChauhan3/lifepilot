import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.tools.python_execution_tool import PythonExecutionTool
from app.tools.web_search_tool import WebSearchTool

@pytest.mark.unit
class TestPythonExecutionToolUnit:
    """Unit tests for PythonExecutionTool"""
    
    def test_execute_simple_code(self):
        """Test executing simple Python code"""
        tool = PythonExecutionTool()
        
        code = "result = 2 + 2\nprint('Sum is:', result)"
        result = tool.execute(code)
        
        assert result["success"] is True
        assert result["result"] == 4
        assert "Sum is: 4" in result["stdout"]
        assert result["error"] is None
    
    def test_execute_with_math_module(self):
        """Test executing code with math module"""
        tool = PythonExecutionTool()
        
        code = "import math\nresult = math.sqrt(16)"
        result = tool.execute(code)
        
        assert result["success"] is True
        assert result["result"] == 4.0
    
    def test_execute_with_error(self):
        """Test executing code with syntax error"""
        tool = PythonExecutionTool()
        
        code = "print('unclosed string"
        result = tool.execute(code)
        
        assert result["success"] is False
        assert result["error"] is not None
        assert "EOL while scanning string literal" in result["error"]
    
    def test_execute_with_variables(self):
        """Test executing code with injected variables"""
        tool = PythonExecutionTool()
        
        code = "result = x + y"
        variables = {"x": 10, "y": 20}
        result = tool.execute(code, variables)
        
        assert result["success"] is True
        assert result["result"] == 30

@pytest.mark.unit
class TestWebSearchToolUnit:
    """Unit tests for WebSearchTool with mocked requests"""
    
    @pytest.fixture
    def web_search_tool(self):
        """Create WebSearchTool instance"""
        return WebSearchTool()
    
    @patch('app.tools.web_search_tool.requests.get')
    def test_search_with_mock(self, mock_get, web_search_tool):
        """Test search without real internet connection"""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "title": "Test Result 1",
                    "link": "https://example.com/1",
                    "snippet": "This is a test result"
                },
                {
                    "title": "Test Result 2",
                    "link": "https://example.com/2",
                    "snippet": "Another test result"
                }
            ]
        }
        mock_get.return_value = mock_response
        
        # Execute
        results = web_search_tool.search("test query", max_results=2)
        
        # Assert
        assert len(results) == 2
        assert results[0]["title"] == "Test Result 1"
        assert results[1]["url"] == "https://example.com/2"
        mock_get.assert_called_once()
    
    @patch('app.tools.web_search_tool.requests.get')
    def test_search_with_error(self, mock_get, web_search_tool):
        """Test search with API error"""
        # Mock error response
        mock_get.side_effect = Exception("Network error")
        
        # Execute
        results = web_search_tool.search("test query")
        
        # Assert - should return empty list on error
        assert results == []
