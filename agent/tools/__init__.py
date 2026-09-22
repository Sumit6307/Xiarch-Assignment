from typing import Dict, List, Optional
from agent.tools.base import BaseTool, ToolResult
from agent.tools.web_search import WebSearchTool
from agent.tools.code_executor import CodeExecutorTool
from agent.tools.file_ops import FileReaderWriterTool
from agent.tools.web_fetcher import WebPageFetcherTool

class ToolRegistry:
    """Registry managing available tools and dispatching execution."""

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self.register_tool(WebSearchTool())
        self.register_tool(CodeExecutorTool())
        self.register_tool(FileReaderWriterTool())
        self.register_tool(WebPageFetcherTool())

    def register_tool(self, tool: BaseTool):
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[BaseTool]:
        return self._tools.get(name)

    def list_tools(self) -> List[Dict[str, str]]:
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "schema": tool.parameters_schema
            }
            for tool in self._tools.values()
        ]

    def set_simulated_failure(self, tool_name: str, enable: bool = True):
        tool = self.get_tool(tool_name)
        if tool:
            tool.set_simulated_failure(enable)

    def execute(self, tool_name: str, kwargs: Dict) -> ToolResult:
        tool = self.get_tool(tool_name)
        if not tool:
            return ToolResult(
                success=False,
                output=None,
                error=f"ToolNotFoundError: Tool '{tool_name}' is not registered."
            )
        try:
            return tool.execute(**kwargs)
        except Exception as e:
            return ToolResult(
                success=False,
                output=None,
                error=f"ToolExecutionException: Unexpected exception in tool '{tool_name}': {str(e)}"
            )
