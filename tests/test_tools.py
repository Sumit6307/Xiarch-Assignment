import os
import pytest
from agent.tools import ToolRegistry
from agent.tools.web_search import WebSearchTool
from agent.tools.code_executor import CodeExecutorTool
from agent.tools.file_ops import FileReaderWriterTool
from agent.tools.web_fetcher import WebPageFetcherTool

def test_tool_registry():
    registry = ToolRegistry()
    tools = registry.list_tools()
    tool_names = [t["name"] for t in tools]
    assert "web_search" in tool_names
    assert "code_executor" in tool_names
    assert "file_ops" in tool_names
    assert "web_fetcher" in tool_names

def test_code_executor_tool():
    tool = CodeExecutorTool()
    res = tool.execute(code="a = 15\nb = 25\nprint(a + b)")
    assert res.success is True
    assert "40" in str(res.output)

def test_code_executor_error_handling():
    tool = CodeExecutorTool()
    res = tool.execute(code="1 / 0")
    assert res.success is False
    assert "ZeroDivisionError" in str(res.error)

def test_file_ops_tool(tmp_path):
    tool = FileReaderWriterTool(base_dir=str(tmp_path))
    # Test Write
    write_res = tool.execute(action="write", filename="test.txt", content="Hello Agentic World")
    assert write_res.success is True
    
    # Test Read
    read_res = tool.execute(action="read", filename="test.txt")
    assert read_res.success is True
    assert read_res.output == "Hello Agentic World"

def test_web_search_tool():
    tool = WebSearchTool()
    res = tool.execute(query="Python Programming Language")
    assert res.success is True
    assert res.output is not None

def test_simulated_failure():
    tool = WebSearchTool()
    tool.set_simulated_failure(True)
    res = tool.execute(query="Python")
    assert res.success is False
    assert "SimulatedToolError" in res.error
