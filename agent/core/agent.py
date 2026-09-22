import time
from typing import Dict, Any, Optional, Callable
from agent.core.memory import AgentMemory, ExecutionStep
from agent.core.llm_provider import BaseLLMProvider, get_llm_provider
from agent.core.planner import Planner
from agent.tools import ToolRegistry, ToolResult

class Agent:
    """Main Agent orchestrating planning, tool execution, self-correction, and reporting."""

    def __init__(
        self,
        llm_provider: Optional[BaseLLMProvider] = None,
        tool_registry: Optional[ToolRegistry] = None,
        max_retries_per_step: int = 2
    ):
        self.tools = tool_registry or ToolRegistry()
        self.llm = llm_provider or get_llm_provider("auto")
        self.planner = Planner(self.llm, self.tools)
        self.max_retries = max_retries_per_step

    def run(
        self,
        goal: str,
        trace_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None
    ) -> AgentMemory:
        """Executes a high-level goal end-to-end with dynamic planning and self-correction."""

        memory = AgentMemory(goal)
        
        def emit_trace(event_type: str, data: Dict[str, Any]):
            if trace_callback:
                trace_callback(event_type, data)

        # Step 1: Initial Planning Phase
        emit_trace("PLANNING_START", {"goal": goal})
        raw_plan = self.planner.create_plan(goal)
        memory.set_plan(raw_plan)
        emit_trace("PLANNING_COMPLETE", {"plan": raw_plan})

        # Step 2: Step-by-Step Execution Phase
        for plan_step in raw_plan:
            step_id = plan_step["step_id"]
            description = plan_step["description"]
            current_tool_name = plan_step["tool_name"]
            current_tool_args = plan_step["tool_args"]

            step_record = ExecutionStep(
                step_id=step_id,
                description=description,
                tool_name=current_tool_name,
                tool_args=current_tool_args
            )

            emit_trace("STEP_START", step_record.to_dict())
            
            step_success = False
            attempts = 0

            while attempts < self.max_retries and not step_success:
                attempts += 1
                step_record.attempts = attempts
                start_time = time.time()

                emit_trace("TOOL_EXECUTION_ATTEMPT", {
                    "step_id": step_id,
                    "attempt": attempts,
                    "tool": current_tool_name,
                    "args": current_tool_args
                })

                # Execute Tool
                result: ToolResult = self.tools.execute(current_tool_name, current_tool_args)
                step_record.execution_time += round(time.time() - start_time, 3)

                if result.success:
                    step_record.status = "RECOVERED" if attempts > 1 else "SUCCESS"
                    step_record.output = str(result.output)
                    step_record.error = None
                    step_success = True
                    emit_trace("TOOL_SUCCESS", {
                        "step_id": step_id,
                        "output": step_record.output,
                        "status": step_record.status
                    })
                else:
                    # Tool Failed -> Trigger Self-Correction Mechanism
                    step_record.status = "FAILED"
                    step_record.error = result.error
                    emit_trace("TOOL_FAILURE", {
                        "step_id": step_id,
                        "error": result.error,
                        "attempt": attempts
                    })

                    if attempts < self.max_retries:
                        emit_trace("SELF_CORRECTION_START", {
                            "step_id": step_id,
                            "failed_tool": current_tool_name,
                            "error": result.error
                        })
                        
                        # Ask Planner for dynamic recovery plan
                        correction = self.planner.revise_plan_on_failure(
                            goal=goal,
                            failed_step={"description": description, "tool_name": current_tool_name},
                            error_msg=result.error or "Unknown tool error",
                            context=memory.get_summary_context()
                        )

                        reflection = correction.get("reflection", "Attempting alternative tool strategy.")
                        step_record.reflection = reflection
                        
                        action_type = correction.get("action", "REPLACE_TOOL")
                        new_tool = correction.get("new_tool_name", "code_executor")
                        new_args = correction.get("new_tool_args", {})

                        # Record self-correction event
                        memory.record_correction(
                            step_id=step_id,
                            failed_tool=current_tool_name,
                            error_msg=result.error or "",
                            recovery_action=f"{action_type} -> {new_tool} ({new_args})"
                        )

                        emit_trace("SELF_CORRECTION_COMPLETE", {
                            "step_id": step_id,
                            "reflection": reflection,
                            "new_tool": new_tool,
                            "new_args": new_args
                        })

                        # Update parameters for retry loop
                        current_tool_name = new_tool
                        current_tool_args = new_args
                        step_record.tool_name = new_tool
                        step_record.tool_args = new_args
                    else:
                        emit_trace("STEP_FAILED_PERMANENTLY", {
                            "step_id": step_id,
                            "final_error": result.error
                        })

            memory.add_step(step_record)

        memory.end_time = time.time()
        emit_trace("EXECUTION_COMPLETE", memory.to_dict())
        return memory
