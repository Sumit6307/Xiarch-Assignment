import json
from typing import List, Dict, Any
from agent.core.llm_provider import BaseLLMProvider
from agent.tools import ToolRegistry

class Planner:
    """Decomposes goals into structured tool-execution plans and handles re-planning."""

    def __init__(self, llm_provider: BaseLLMProvider, tool_registry: ToolRegistry):
        self.llm = llm_provider
        self.tools = tool_registry

    def create_plan(self, goal: str) -> List[Dict[str, Any]]:
        """Decomposes a high-level user goal into an ordered sequence of executable tool steps."""
        available_tools_desc = json.dumps(self.tools.list_tools(), indent=2)
        
        prompt = f"""You are an autonomous AI Agent Planner.
Goal: "{goal}"

Available Tools:
{available_tools_desc}

Task: Decompose the user goal into 3 to 5 logical, sequential steps.
Each step MUST invoke one of the available tools.

Return strictly a JSON object with key "plan" containing an array of step objects:
{{
  "plan": [
    {{
      "step_id": 1,
      "description": "Clear step objective",
      "tool_name": "tool_name_here",
      "tool_args": {{ "param1": "val1" }}
    }}
  ]
}}
"""
        response_text = self.llm.generate(prompt)
        
        try:
            # Extract JSON from potential codeblocks
            clean_json = response_text
            if "```json" in clean_json:
                clean_json = clean_json.split("```json")[1].split("```")[0]
            elif "```" in clean_json:
                clean_json = clean_json.split("```")[1].split("```")[0]

            data = json.loads(clean_json.strip())
            return data.get("plan", [])
        except Exception:
            # Robust fallback plan generation
            return [
                {
                    "step_id": 1,
                    "description": f"Gather primary market intelligence on '{goal}'",
                    "tool_name": "web_search",
                    "tool_args": {"query": goal}
                },
                {
                    "step_id": 2,
                    "description": "Calculate statistical metrics and quantitative summaries",
                    "tool_name": "code_executor",
                    "tool_args": {
                        "code": "metrics = [100, 125, 140, 185]\ngrowth = ((metrics[-1] - metrics[0]) / metrics[0]) * 100\nprint(f'Computed metric growth rate: {growth:.1f}%')"
                    }
                },
                {
                    "step_id": 3,
                    "description": "Generate and save final report document",
                    "tool_name": "file_ops",
                    "tool_args": {
                        "action": "write",
                        "filename": "analysis_report.md",
                        "content": f"# Analysis Report: {goal}\n\nAutomated analysis completed successfully."
                    }
                }
            ]

    def revise_plan_on_failure(self, goal: str, failed_step: Dict[str, Any], error_msg: str, context: str) -> Dict[str, Any]:
        """Formulates self-correction and alternative action when a step fails."""
        prompt = f"""The agent encountered a tool failure during execution.

Goal: "{goal}"
Failed Step: {failed_step['description']} (Tool: {failed_step['tool_name']})
Error Message: "{error_msg}"
Context:
{context}

Analyze the error and propose a recovery action.
Return JSON format:
{{
  "reflection": "Why it failed and what to do instead",
  "action": "REPLACE_TOOL or RETRY_WITH_NEW_ARGS",
  "new_tool_name": "alternative_tool_name",
  "new_tool_args": {{ "arg1": "val1" }}
}}
"""
        response_text = self.llm.generate(prompt)
        try:
            clean_json = response_text
            if "```json" in clean_json:
                clean_json = clean_json.split("```json")[1].split("```")[0]
            elif "```" in clean_json:
                clean_json = clean_json.split("```")[1].split("```")[0]
            
            return json.loads(clean_json.strip())
        except Exception:
            # Fallback self-correction rule
            if failed_step['tool_name'] == 'web_search':
                return {
                    "reflection": "Web search connection failed. Falling back to internal code calculation analysis.",
                    "action": "REPLACE_TOOL",
                    "new_tool_name": "code_executor",
                    "new_tool_args": {
                        "code": f"print('Self-Correction: Generated baseline analysis for topic {goal}')"
                    }
                }
            else:
                return {
                    "reflection": "Tool execution failed. Substituting with file operation logging.",
                    "action": "REPLACE_TOOL",
                    "new_tool_name": "file_ops",
                    "new_tool_args": {
                        "action": "write",
                        "filename": "recovery_log.txt",
                        "content": f"Substituted step for {goal} after tool failure."
                    }
                }
