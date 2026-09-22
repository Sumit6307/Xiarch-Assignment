import time
from typing import List, Dict, Any, Optional

class ExecutionStep:
    """Dataclass holding information for a single step in the agent's plan."""
    def __init__(self, step_id: int, description: str, tool_name: str, tool_args: Dict[str, Any]):
        self.step_id = step_id
        self.description = description
        self.tool_name = tool_name
        self.tool_args = tool_args
        self.status = "PENDING"  # PENDING, EXECUTING, SUCCESS, FAILED, RECOVERED
        self.output: Optional[str] = None
        self.error: Optional[str] = None
        self.thought: Optional[str] = None
        self.reflection: Optional[str] = None
        self.attempts: int = 0
        self.execution_time: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_id": self.step_id,
            "description": self.description,
            "tool_name": self.tool_name,
            "tool_args": self.tool_args,
            "status": self.status,
            "output": self.output,
            "error": self.error,
            "thought": self.thought,
            "reflection": self.reflection,
            "attempts": self.attempts,
            "execution_time": self.execution_time
        }


class AgentMemory:
    """Manages short-term and working memory across agent execution steps."""
    def __init__(self, goal: str):
        self.goal = goal
        self.plan: List[Dict[str, Any]] = []
        self.history: List[ExecutionStep] = []
        self.self_corrections: List[Dict[str, Any]] = []
        self.start_time = time.time()
        self.end_time: Optional[float] = None

    def set_plan(self, plan: List[Dict[str, Any]]):
        self.plan = plan

    def add_step(self, step: ExecutionStep):
        self.history.append(step)

    def record_correction(self, step_id: int, failed_tool: str, error_msg: str, recovery_action: str):
        self.self_corrections.append({
            "step_id": step_id,
            "failed_tool": failed_tool,
            "error_msg": error_msg,
            "recovery_action": recovery_action,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        })

    def get_summary_context(self) -> str:
        """Summarizes executed steps for LLM prompt context."""
        ctx_lines = [f"Goal: {self.goal}"]
        for step in self.history:
            if step.status == "SUCCESS":
                ctx_lines.append(f"- Step {step.step_id} ({step.description}) -> SUCCESS: {str(step.output)[:250]}")
            elif step.status in ("FAILED", "RECOVERED"):
                ctx_lines.append(f"- Step {step.step_id} ({step.description}) -> {step.status}: {step.error or step.output}")
        return "\n".join(ctx_lines)

    def to_dict(self) -> Dict[str, Any]:
        duration = (self.end_time or time.time()) - self.start_time
        return {
            "goal": self.goal,
            "duration_seconds": round(duration, 2),
            "plan_count": len(self.plan),
            "steps_executed": [step.to_dict() for step in self.history],
            "self_corrections": self.self_corrections,
            "total_attempts": sum(s.attempts for s in self.history)
        }
