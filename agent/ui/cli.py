import sys
import argparse
from typing import Optional
from agent.core.agent import Agent
from agent.tools import ToolRegistry
from agent.utils.logger import TraceLogger
from agent.utils.report_generator import ReportGenerator

def run_cli():
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass

    parser = argparse.ArgumentParser(
        description="Functional Agentic AI System CLI - Autonomous Goal Planning & Tool Execution"
    )
    parser.add_argument(
        "--goal",
        type=str,
        default="Research recent AI developments, run calculations, and generate a report",
        help="Natural language goal prompt for the agent to accomplish."
    )
    parser.add_argument(
        "--simulate-failure",
        type=str,
        default=None,
        choices=["web_search", "web_fetcher", "code_executor", "file_ops"],
        help="Induce a simulated failure for the specified tool to evaluate self-correction recovery."
    )
    parser.add_argument(
        "--provider",
        type=str,
        default="auto",
        choices=["auto", "groq", "gemini", "openai", "mock"],
        help="LLM Provider backend (auto detects GROQ_API_KEY, GEMINI_API_KEY, OPENAI_API_KEY or defaults to mock engine)."
    )

    args = parser.parse_args()

    print("\n=======================================================")
    print("🤖 Agentic AI System - Goal Execution Engine")
    print("=======================================================\n")

    registry = ToolRegistry()
    if args.simulate_failure:
        print(f"⚠️  SIMULATING INDUCED FAILURE FOR TOOL: '{args.simulate_failure}'")
        registry.set_simulated_failure(args.simulate_failure, True)

    from agent.core.llm_provider import get_llm_provider
    agent = Agent(llm_provider=get_llm_provider(args.provider), tool_registry=registry)
    
    # Run Agent with live visual trace logger callback
    memory = agent.run(goal=args.goal, trace_callback=TraceLogger.on_event)

    # Export Reports
    json_rep = ReportGenerator.generate_json_report(memory, "output/final_report.json")
    md_rep = ReportGenerator.generate_markdown_report(memory, "output/final_report.md")

    print("\n-------------------------------------------------------")
    print("✅ EXECUTION FINISHED")
    print("📁 Reports saved:")
    print("   - JSON Report:     output/final_report.json")
    print("   - Markdown Report: output/final_report.md")
    print("-------------------------------------------------------\n")

if __name__ == "__main__":
    run_cli()
