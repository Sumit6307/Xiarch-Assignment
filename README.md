# 🤖 Autonomous Agentic AI System

> **A functional, self-correcting Agentic AI System built with dynamic goal decomposition, multi-tool orchestration, robust failure recovery, visual execution tracing, and structured reporting.**

---

## 🌟 Key Features

- 🎯 **Autonomous Goal Decomposition**: Accepts high-level natural language prompts and dynamically breaks them down into a visible, structured sequence of execution steps before taking action.
- 🧰 **Multi-Tool Orchestration (4 Distinct Tools)**:
  1. `WebSearchTool`: Searches live web data using DuckDuckGo API with direct HTTP HTML parsing fallback.
  2. `WebPageFetcherTool`: Fetches raw HTML and extracts clean readable text from URLs.
  3. `CodeExecutorTool`: Safe Python sandbox for mathematical calculations, data formatting, and statistical processing.
  4. `FileReaderWriterTool`: Manages persistent workspace files and formats executive reports.
- 🔄 **Self-Correction & Dynamic Recovery**:
  - Automatically intercepts tool execution errors (timeouts, 403 access blocks, execution exceptions).
  - Triggers a reflection prompt and dynamic re-planning engine to either retry with sanitized parameters or substitute an alternative tool.
  - Features an explicit `--simulate-failure <tool_name>` CLI flag to deliberately induce and demonstrate self-correction in real time.
- 🖥️ **Dual User Interfaces**:
  - **Rich CLI**: Features colored terminal output, interactive step panels, and trace spinners.
  - **Streamlit Web Studio**: Full web dashboard displaying visual planning graphs, live step progress, execution timelines, and report download buttons.
- 📝 **Structured Output Generation**: Produces complete, standardized JSON (`output/final_report.json`) and formatted Markdown (`output/final_report.md`) executive reports.
- 🔑 **LLM Provider Agnostic**: Works out-of-the-box with OpenAI (`OPENAI_API_KEY`) or an offline zero-dependency `HeuristicMockLLM` fallback engine.

---

## 🏗️ Architecture Diagram

```
                              ┌──────────────────────────┐
                              │ User / CLI / Streamlit UI│
                              └────────────┬─────────────┘
                                           │ Goal Prompt
                                           ▼
                    ┌──────────────────────────────────────────────┐
                    │          Core Agent Execution Engine         │
                    │                                              │
                    │   ┌──────────────┐      ┌────────────────┐   │
                    │   │  Planner &   │      │ Self-Correction│   │
                    │   │ Decomposer   │◄────►│  & Reflection  │   │
                    │   └──────┬───────┘      └────────────────┘   │
                    │          │                       ▲           │
                    │          ▼                       │           │
                    │   ┌──────────────┐               │           │
                    │   │Working Memory│               │           │
                    │   └──────────────┘               │           │
                    └──────────┬───────────────────────┼───────────┘
                               │ Step Plan             │ Tool Error
                               ▼                       │
                    ┌──────────────────────────────────┴───────────┐
                    │         Multi-Tool Registry Engine           │
                    │                                              │
                    │  ┌────────────┐ ┌─────────────┐ ┌─────────┐  │
                    │  │ Web Search │ │ Web Fetcher │ │Code Exec│  │
                    │  └────────────┘ └─────────────┘ └─────────┘  │
                    │  ┌────────────┐                              │
                    │  │  File Ops  │                              │
                    │  └────────────┘                              │
                    └──────────┬───────────────────────────────────┘
                               │ Final Outputs
                               ▼
                    ┌──────────────────────────────────────────────┐
                    │ output/final_report.json & final_report.md   │
                    └──────────────────────────────────────────────┘
```

Visual diagram available at [`docs/architecture_diagram.png`](file:///c:/Local%20Disk%20-%20D/AII-New-Assignment/Xiarch-Assignment/docs/architecture_diagram.png) and [`docs/architecture.mermaid`](file:///c:/Local%20Disk%20-%20D/AII-New-Assignment/Xiarch-Assignment/docs/architecture.mermaid).

---

## ⚡ Quick Start & Setup

### 1. Prerequisites
- Python **3.9+** installed.

### 2. Installation
Clone the repository and install required dependencies:
```bash
# Install dependencies
pip install -r requirements.txt
```

*(Optional) Set your OpenAI API Key if you wish to use live LLM models:*
```bash
# Windows PowerShell
$env:OPENAI_API_KEY="your-api-key-here"

# Linux / macOS
export OPENAI_API_KEY="your-api-key-here"
```
*Note: If no API key is set, the system automatically runs using its built-in intelligent offline engine!*

---

## 🚀 Running the Agent

### A. Run via CLI (Terminal)

#### 1. Basic Execution
```bash
python main.py --goal "Research Stripe metrics, compute growth rate, and generate report"
```

#### 2. Induced Failure & Self-Correction Test
Deliberately fail a tool (e.g. `web_search`) to evaluate how the agent dynamically reflects, swaps tools, and recovers:
```bash
python main.py --goal "Research competitor market share" --simulate-failure web_search
```

### B. Run via Web Dashboard (Streamlit)

Launch the interactive web application:
```bash
streamlit run agent/ui/app.py
```
Open your browser at `http://localhost:8501` to view live execution traces, progress timers, and download final reports.

---

## 🧪 Running the Test Suite

Run the full automated test suite covering unit tool tests, agent execution, and self-correction recovery:
```bash
python -m pytest tests/ -v
```

---

## 📁 Repository Structure

```
Xiarch-Assignment/
├── agent/
│   ├── core/
│   │   ├── agent.py            # ReAct Loop & Agent Engine
│   │   ├── planner.py          # Dynamic Goal Decomposition & Re-planning
│   │   ├── memory.py           # Execution History & Working Memory State
│   │   └── llm_provider.py     # OpenAI / Gemini / Mock LLM Bridge
│   ├── tools/
│   │   ├── base.py             # Tool Base Class & ToolResult Schema
│   │   ├── web_search.py       # DuckDuckGo & Live HTTP Search Tool
│   │   ├── web_fetcher.py      # HTML Scraper & Webpage Content Fetcher
│   │   ├── code_executor.py    # Python Math Sandbox & Code Engine
│   │   ├── file_ops.py         # File Reader & Report Writer Tool
│   │   └── __init__.py         # Tool Registry Engine
│   ├── utils/
│   │   ├── logger.py           # Rich Visual Trace Formatting
│   │   └── report_generator.py # Structured JSON & Markdown Report Builder
│   └── ui/
│       ├── cli.py              # CLI Interface Runner
│       └── app.py              # Streamlit Interactive Web Application
├── tests/
│   ├── test_tools.py           # Unit tests for all 4 tools
│   ├── test_agent.py           # End-to-end agent execution tests
│   └── test_self_correction.py # Induced failure recovery verification
├── transcripts/                # Execution traces & sample logs
│   ├── sample_run_1_research.md
│   ├── sample_run_2_failure_recovery.md
│   └── sample_run_3_code_analysis.md
├── docs/
│   ├── architecture_diagram.png # Exported Architecture Diagram
│   └── architecture.mermaid    # Mermaid flowchart source
├── main.py                     # Primary CLI Entrypoint
├── writeup.md                  # Technical design summary & trade-offs
├── requirements.txt            # Package dependencies
└── README.md                   # Project Documentation
```

---

## 📄 Deliverables Summary

| Deliverable | Location | Description |
| :--- | :--- | :--- |
| **Source Code** | Entire Repo | Fully modular Python framework with CLI & Web UI |
| **Architecture Diagram** | [`docs/architecture_diagram.png`](file:///c:/Local%20Disk%20-%20D/AII-New-Assignment/Xiarch-Assignment/docs/architecture_diagram.png) | Visual PNG diagram & Mermaid schema |
| **Sample Transcripts** | [`transcripts/`](file:///c:/Local%20Disk%20-%20D/AII-New-Assignment/Xiarch-Assignment/transcripts) | 3 complete execution logs (standard, induced failure, code run) |
| **Design Write-up** | [`writeup.md`](file:///c:/Local%20Disk%20-%20D/AII-New-Assignment/Xiarch-Assignment/writeup.md) | Technical decisions, limitations, and future improvements |
