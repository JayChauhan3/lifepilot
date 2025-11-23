import structlog
import sys
import io
import traceback
from typing import Dict, Any, Optional

logger = structlog.get_logger()

class PythonExecutionTool:
    """Tool for executing Python code safely"""
    
    def __init__(self):
        logger.info("PythonExecutionTool initialized")
    
    def execute(self, code: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute Python code and return the result, stdout, and any errors.
        
        Args:
            code: The Python code to execute
            variables: Optional dictionary of variables to inject into the execution context
            
        Returns:
            Dict containing 'result', 'stdout', 'error', and 'success' status
        """
        logger.info("Executing Python code", code_length=len(code))
        
        # Capture stdout
        old_stdout = sys.stdout
        redirected_output = io.StringIO()
        sys.stdout = redirected_output
        
        # Prepare execution context
        local_vars = variables or {}
        global_vars = {"__builtins__": __builtins__, "math": __import__("math"), "datetime": __import__("datetime")}
        
        result = None
        error = None
        success = False
        
        try:
            # Execute the code
            exec(code, global_vars, local_vars)
            
            # If the code defines a 'result' variable, use that as the return value
            if 'result' in local_vars:
                result = local_vars['result']
            
            success = True
            logger.info("Python execution successful")
            
        except Exception as e:
            error = str(e)
            # Get traceback for detailed error
            tb = traceback.format_exc()
            logger.error("Python execution failed", error=error)
            # Append traceback to stdout for debugging
            print(f"\nError: {error}\n{tb}")
            
        finally:
            # Restore stdout
            sys.stdout = old_stdout
            
        output = redirected_output.getvalue()
        
        return {
            "result": result,
            "stdout": output,
            "error": error,
            "success": success
        }
