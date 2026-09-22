import sys
import io
import math
import json
import traceback
from typing import Dict, Any
from agent.tools.base import BaseTool, ToolResult

class CodeExecutorTool(BaseTool):
    """Tool for safely executing Python code snippets, mathematical calculations, and data processing."""

    def __init__(self):
        super().__init__(
            name="code_executor",
            description="Executes a snippet of Python code for mathematical calculations, data formatting, and logic.",
            parameters_schema={
                "code": "The raw Python code string to execute. Use print() to output results."
            }
        )

    def execute(self, code: str = "", **kwargs) -> ToolResult:
        if self.simulated_failure:
            return ToolResult(
                success=False,
                output=None,
                error="SimulatedToolError: MemoryLimitExceeded during code execution."
            )

        if not code or not code.strip():
            return ToolResult(
                success=False,
                output=None,
                error="InvalidInputError: Code snippet cannot be empty."
            )

        clean_code = code.strip()
        
        # Setup stdout redirection
        old_stdout = sys.stdout
        redirected_output = io.StringIO()
        sys.stdout = redirected_output

        safe_globals = {
            "__builtins__": {
                "abs": abs, "all": all, "any": any, "bin": bin, "bool": bool, "dict": dict,
                "enumerate": enumerate, "filter": filter, "float": float, "format": format,
                "int": int, "isinstance": isinstance, "len": len, "list": list, "map": map,
                "max": max, "min": min, "pow": pow, "print": print, "range": range,
                "round": round, "set": set, "sorted": sorted, "str": str, "sum": sum,
                "tuple": tuple, "zip": zip, "json": json, "__import__": __import__
            },
            "math": math,
            "re": re
        }
        
        local_scope: Dict[str, Any] = {}

        try:
            exec(clean_code, safe_globals, local_scope)
            printed_output = redirected_output.getvalue().strip()
            
            # Find any assigned return variables if no print statement was used
            result_str = printed_output
            if not result_str and local_scope:
                # Get last mutated variable
                last_var = list(local_scope.keys())[-1]
                result_str = f"{last_var} = {local_scope[last_var]}"

            if not result_str:
                result_str = "Code executed successfully with no output."

            return ToolResult(
                success=True,
                output=result_str,
                metadata={"scope_keys": list(local_scope.keys())}
            )
        except Exception as e:
            tb = traceback.format_exc()
            return ToolResult(
                success=False,
                output=None,
                error=f"ExecutionError: {type(e).__name__}: {str(e)}\nTraceback:\n{tb[-300:]}"
            )
        finally:
            sys.stdout = old_stdout
