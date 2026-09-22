import streamlit as st
import json
import time
import os
import sys

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from agent.core.agent import Agent
from agent.tools import ToolRegistry
from agent.utils.report_generator import ReportGenerator

st.set_page_config(
    page_title="Agentic AI Studio",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-title {
        font-size: 2.3rem;
        font-weight: 700;
        background: linear-gradient(90deg, #4F46E5 0%, #06B6D4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .stAlert {
        border-radius: 8px;
    }
    .metric-box {
        background-color: #1E293B;
        padding: 1rem;
        border-radius: 8px;
        color: #F8FAFC;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🤖 Agentic AI System Studio</div>', unsafe_allow_html=True)
st.caption("Autonomous Goal Decomposition • Multi-Tool Orchestration • Self-Correction & Robustness")

# Sidebar Configuration
st.sidebar.header("⚙️ Agent Settings")
provider_option = st.sidebar.selectbox("LLM Provider", ["Auto-Detect (Groq/Gemini/OpenAI/Mock)", "Google Gemini", "Groq Cloud", "OpenAI", "Heuristic Mock Engine"])
simulate_failure_option = st.sidebar.selectbox(
    "Induce Simulated Failure",
    ["None (Normal Mode)", "web_search", "web_fetcher", "code_executor", "file_ops"],
    help="Select a tool to deliberately fail during execution to demonstrate automatic self-correction recovery."
)

st.sidebar.markdown("---")
st.sidebar.subheader("🛠️ Available Tools")
st.sidebar.markdown("""
- **🌐 Web Search**: DDG / HTTP live query aggregator
- **📄 Web Fetcher**: HTML scraper & content extractor
- **💻 Code Executor**: Python sandbox & math evaluator
- **📁 File Ops**: Report writer & workspace file reader
""")

# Sample Goals
example_goals = [
    "Research company Stripe metrics, compute growth rate, and write a market analysis report.",
    "Research top 3 developments in AI Agents this week and save a summary file.",
    "Given a 5-step data calculation task, evaluate statistics using python code executor."
]

selected_example = st.selectbox("💡 Quick Sample Goals:", ["Select a prompt or write custom below..."] + example_goals)
default_text = selected_example if selected_example != "Select a prompt or write custom below..." else ""

user_goal = st.text_area("🎯 Enter Goal Prompt:", value=default_text, height=100, placeholder="e.g. Research competitor landscape for SpaceX...")

run_button = st.button("🚀 Run Agentic Workflow", type="primary", use_container_width=True)

if run_button and user_goal:
    registry = ToolRegistry()
    if simulate_failure_option != "None (Normal Mode)":
        registry.set_simulated_failure(simulate_failure_option, True)
        st.warning(f"⚠️ Induced failure active for tool: `{simulate_failure_option}`")

    from agent.core.llm_provider import get_llm_provider

    provider_map = {
        "Auto-Detect (Groq/Gemini/OpenAI/Mock)": "auto",
        "Google Gemini": "gemini",
        "Groq Cloud": "groq",
        "OpenAI": "openai",
        "Heuristic Mock Engine": "mock"
    }
    p_code = provider_map.get(provider_option, "auto")

    agent = Agent(llm_provider=get_llm_provider(p_code), tool_registry=registry)

    # UI Containers for visual trace
    trace_container = st.container()
    trace_logs = []
    
    status_placeholder = st.empty()
    progress_bar = st.progress(0)

    with status_placeholder.container():
        st.info("🔄 Agent initializing and planning...")

    step_status_area = st.empty()
    
    def ui_trace_callback(event_type: str, data: dict):
        trace_logs.append((event_type, data))
        if event_type == "PLANNING_COMPLETE":
            with step_status_area.container():
                st.subheader("📋 Generated Step Plan")
                plan_df = [
                    {"Step": s.get("step_id"), "Objective": s.get("description"), "Tool": s.get("tool_name"), "Args": str(s.get("tool_args"))}
                    for s in data["plan"]
                ]
                st.table(plan_df)
        elif event_type == "TOOL_EXECUTION_ATTEMPT":
            progress_bar.progress(0.4)
        elif event_type == "SELF_CORRECTION_COMPLETE":
            st.error(f"🔄 **Self-Correction Triggered!** Reflection: *{data.get('reflection')}* → Swapped to tool `{data.get('new_tool')}`")

    # Run Execution
    start_t = time.time()
    try:
        memory = agent.run(goal=user_goal, trace_callback=ui_trace_callback)
        duration = round(time.time() - start_t, 2)

        progress_bar.progress(1.0)
        status_placeholder.success(f"✨ Goal Execution Finished in {duration} seconds!")

        # Tabs for Outputs
        tab_report, tab_trace, tab_metrics, tab_raw = st.tabs(["📄 Final Report", "🔍 Execution Trace", "📈 Metrics & Self-Correction", "📦 Raw JSON"])

        json_report = ReportGenerator.generate_json_report(memory, "output/final_report.json")
        md_report = ReportGenerator.generate_markdown_report(memory, "output/final_report.md")

        with tab_report:
            st.markdown(md_report)
            st.download_button(
                label="📥 Download Markdown Report",
                data=md_report,
                file_name="final_report.md",
                mime="text/markdown"
            )

        with tab_trace:
            st.subheader("🕵️ Step-by-Step ReAct Log")
            for step in memory.history:
                badge = "✅ SUCCESS" if step.status == "SUCCESS" else ("⚡ RECOVERED" if step.status == "RECOVERED" else "❌ FAILED")
                with st.expander(f"Step {step.step_id}: {step.description} [{badge}]", expanded=True):
                    st.markdown(f"**Tool:** `{step.tool_name}` | **Attempts:** `{step.attempts}` | **Time:** `{step.execution_time}s`")
                    if step.reflection:
                        st.info(f"💡 **Reflection / Recovery:** {step.reflection}")
                    st.code(step.output or step.error or "No output", language="text")

        with tab_metrics:
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Duration", f"{duration}s")
            col2.metric("Total Steps", len(memory.plan))
            col3.metric("Self-Corrections", len(memory.self_corrections))
            col4.metric("Total Attempts", sum(s.attempts for s in memory.history))

            if memory.self_corrections:
                st.subheader("🔄 Self-Correction Events")
                st.json(memory.self_corrections)

        with tab_raw:
            st.json(json_report)
    except Exception as err:
        status_placeholder.error(f"❌ Execution Error: {str(err)}")
        st.warning("💡 **Tip**: If using OpenAI or Gemini without an API key, select **Groq Cloud** or **Auto-Detect** in the sidebar!")
