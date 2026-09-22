import os
import json
from typing import Dict, Any
from agent.core.memory import AgentMemory

class ReportGenerator:
    """Generates structured Markdown and JSON reports summarizing agent execution."""

    @staticmethod
    def generate_json_report(memory: AgentMemory, output_path: str = "output/final_report.json") -> Dict[str, Any]:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        report_data = {
            "status": "COMPLETED",
            "goal": memory.goal,
            "metrics": {
                "duration_seconds": round((memory.end_time or 0) - memory.start_time, 2),
                "total_steps": len(memory.plan),
                "successful_steps": sum(1 for s in memory.history if s.status in ("SUCCESS", "RECOVERED")),
                "failed_steps": sum(1 for s in memory.history if s.status == "FAILED"),
                "self_corrections_count": len(memory.self_corrections)
            },
            "planning_trace": memory.plan,
            "execution_history": [step.to_dict() for step in memory.history],
            "self_corrections": memory.self_corrections
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2)
        return report_data

    @staticmethod
    def generate_markdown_report(memory: AgentMemory, output_path: str = "output/final_report.md") -> str:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        duration = round((memory.end_time or 0) - memory.start_time, 2)
        success_count = sum(1 for s in memory.history if s.status in ("SUCCESS", "RECOVERED"))

        md = [
            f"# 🤖 Agentic AI Execution Report",
            f"**Goal:** {memory.goal}\n",
            f"## 📊 Executive Summary",
            f"- **Execution Status:** COMPLETED",
            f"- **Total Duration:** `{duration} seconds`",
            f"- **Total Steps Planned:** `{len(memory.plan)}`",
            f"- **Steps Successfully Executed:** `{success_count}/{len(memory.plan)}`",
            f"- **Self-Correction Triggered:** `{len(memory.self_corrections)} time(s)`\n",
            f"---",
            f"## 🧩 1. Initial Planning Trace",
            f"The agent decomposed the goal into the following structured plan:\n"
        ]

        for step in memory.plan:
            md.append(f"1. **Step {step.get('step_id')}**: {step.get('description')}  ")
            md.append(f"   - *Tool:* `{step.get('tool_name')}` | *Args:* `{json.dumps(step.get('tool_args'))}`")

        md.append(f"\n---")
        md.append(f"## ⚙ 2. Execution & Tool Trace")

        for step in memory.history:
            status_badge = "✅ SUCCESS" if step.status == "SUCCESS" else ("⚡ RECOVERED" if step.status == "RECOVERED" else "❌ FAILED")
            md.append(f"### Step {step.step_id}: {step.description}")
            md.append(f"- **Status:** {status_badge}")
            md.append(f"- **Tool Used:** `{step.tool_name}` (Attempt {step.attempts})")
            md.append(f"- **Execution Time:** `{step.execution_time}s`")
            
            if step.reflection:
                md.append(f"- **Self-Correction Note:** *{step.reflection}*")
                
            md.append("\n**Output / Result:**")
            md.append(f"```")
            out_text = str(step.output or step.error or "No output")
            if len(out_text) > 1000:
                out_text = out_text[:1000] + "\n...[truncated]"
            md.append(out_text)
            md.append("```\n")

        if memory.self_corrections:
            md.append("---")
            md.append("## 🔄 3. Self-Correction & Robustness Log")
            md.append("The agent encountered tool errors and dynamically self-corrected:\n")
            for sc in memory.self_corrections:
                md.append(f"- **Step {sc['step_id']}**: Tool `{sc['failed_tool']}` failed with error: `{sc['error_msg']}`")
                md.append(f"  - **Recovery Action:** `{sc['recovery_action']}` at `{sc['timestamp']}`")

        md_content = "\n".join(md)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(md_content)

        return md_content
