import os
import sys
import json
sys.path.insert(0, ".")
from agent.core.agent import Agent
from agent.tools import ToolRegistry
from agent.utils.report_generator import ReportGenerator

def generate_sample_transcripts():
    os.makedirs("transcripts", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    # ----------------------------------------------------
    # Sample Run 1: End-to-End Market Research Task
    # ----------------------------------------------------
    print("Executing Sample Run 1: Market Research...")
    agent1 = Agent()
    goal1 = "Research top 3 developments in AI Agents this week and write an executive brief."
    mem1 = agent1.run(goal=goal1)
    
    t1_md = [
        "# Sample Run 1: End-to-End Market Research Task",
        f"**Goal:** {goal1}\n",
        "## 1. Initial Goal Planning Trace",
        "```json",
        json.dumps(mem1.plan, indent=2),
        "```\n",
        "## 2. Execution & Tool Trace",
    ]
    for s in mem1.history:
        t1_md.append(f"### Step {s.step_id}: {s.description}")
        t1_md.append(f"- **Tool:** `{s.tool_name}` | **Status:** `{s.status}` | **Duration:** `{s.execution_time}s`")
        t1_md.append(f"```\n{s.output or s.error}\n```\n")
    
    with open("transcripts/sample_run_1_research.md", "w", encoding="utf-8") as f:
        f.write("\n".join(t1_md))

    # ----------------------------------------------------
    # Sample Run 2: Induced Failure & Self-Correction Recovery
    # ----------------------------------------------------
    print("Executing Sample Run 2: Induced Failure Self-Correction...")
    reg2 = ToolRegistry()
    reg2.set_simulated_failure("web_search", True) # Induce failure
    agent2 = Agent(tool_registry=reg2)
    goal2 = "Research competitor valuation metrics for Stripe and synthesize findings."
    mem2 = agent2.run(goal=goal2)

    t2_md = [
        "# Sample Run 2: Induced Failure & Automatic Self-Correction Recovery",
        f"**Goal:** {goal2}",
        "**Note:** Deliberate failure induced on `web_search` tool to evaluate robustness and dynamic re-planning.\n",
        "## 1. Goal Planning Trace",
        "```json",
        json.dumps(mem2.plan, indent=2),
        "```\n",
        "## 2. Failure & Self-Correction Log",
    ]
    for sc in mem2.self_corrections:
        t2_md.append(f"❌ **Tool Failure:** `{sc['failed_tool']}` threw: `{sc['error_msg']}`")
        t2_md.append(f"🔄 **Recovery Action:** `{sc['recovery_action']}`\n")

    t2_md.append("## 3. Final Execution Trace")
    for s in mem2.history:
        status_label = "⚡ RECOVERED" if s.status == "RECOVERED" else s.status
        t2_md.append(f"### Step {s.step_id}: {s.description} [{status_label}]")
        t2_md.append(f"- **Final Tool Used:** `{s.tool_name}` (Attempt {s.attempts})")
        if s.reflection:
            t2_md.append(f"- **Reflection Note:** *{s.reflection}*")
        t2_md.append(f"```\n{s.output}\n```\n")

    with open("transcripts/sample_run_2_failure_recovery.md", "w", encoding="utf-8") as f:
        f.write("\n".join(t2_md))

    # ----------------------------------------------------
    # Sample Run 3: Python Code Execution & File Operations
    # ----------------------------------------------------
    print("Executing Sample Run 3: Statistical Code & File Analysis...")
    agent3 = Agent()
    goal3 = "Calculate quarterly growth rates from dataset [120, 145, 170, 210] and write summary file."
    mem3 = agent3.run(goal=goal3)

    t3_md = [
        "# Sample Run 3: Statistical Code Calculation & File Reporting Task",
        f"**Goal:** {goal3}\n",
        "## 1. Goal Planning Trace",
        "```json",
        json.dumps(mem3.plan, indent=2),
        "```\n",
        "## 2. Tool Execution Output",
    ]
    for s in mem3.history:
        t3_md.append(f"### Step {s.step_id}: {s.description}")
        t3_md.append(f"- **Tool:** `{s.tool_name}` | **Status:** `{s.status}`")
        t3_md.append(f"```\n{s.output}\n```\n")

    with open("transcripts/sample_run_3_code_analysis.md", "w", encoding="utf-8") as f:
        f.write("\n".join(t3_md))

    print("Transcripts successfully generated in transcripts/")

if __name__ == "__main__":
    generate_sample_transcripts()
