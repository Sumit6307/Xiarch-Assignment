import abc
from typing import Any, Dict, Optional

class ToolResult:
    """Standard container for tool execution output."""
    def __init__(self, success: bool, output: Any, error: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):
        self.success = success
        self.output = output
        self.error = error
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "output": str(self.output),
            "error": self.error,
            "metadata": self.metadata
        }

    def __repr__(self) -> str:
        if self.success:
            return f"ToolResult(success=True, output={str(self.output)[:100]}...)"
        return f"ToolResult(success=False, error={self.error})"


class BaseTool(abc.ABC):
    """Abstract Base Class for all Agent Tools."""
    
    def __init__(self, name: str, description: str, parameters_schema: Dict[str, Any]):
        self.name = name
        self.description = description
        self.parameters_schema = parameters_schema
        self.simulated_failure: bool = False

    def set_simulated_failure(self, enable: bool = True):
        """Allows test runner to induce failure for robust error handling tests."""
        self.simulated_failure = enable

    @abc.abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """Executes tool logic and returns a ToolResult."""
        pass
