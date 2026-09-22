import pytest
from agent.core.agent import Agent
from agent.tools import ToolRegistry

def test_agent_end_to_end():
    agent = Agent()
    goal = "Research AI Agents, run statistical calculation, and save report."
    memory = agent.run(goal=goal)
    
    assert memory.goal == goal
    assert len(memory.plan) >= 2
    assert len(memory.history) == len(memory.plan)
    
    # Check that steps completed
    successful_steps = [s for s in memory.history if s.status in ("SUCCESS", "RECOVERED")]
    assert len(successful_steps) > 0
