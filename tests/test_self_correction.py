import pytest
from agent.core.agent import Agent
from agent.tools import ToolRegistry

def test_self_correction_on_tool_failure():
    registry = ToolRegistry()
    # Deliberately induce failure on web_search tool
    registry.set_simulated_failure("web_search", True)

    agent = Agent(tool_registry=registry)
    goal = "Research company valuation metrics and summarize output"

    memory = agent.run(goal=goal)

    # Verify self-correction was triggered and recorded
    assert len(memory.self_corrections) > 0
    sc = memory.self_corrections[0]
    assert sc["failed_tool"] == "web_search"
    assert "SimulatedToolError" in sc["error_msg"]

    # Verify that despite the tool failure, step status became RECOVERED
    recovered_steps = [s for s in memory.history if s.status == "RECOVERED"]
    assert len(recovered_steps) > 0
