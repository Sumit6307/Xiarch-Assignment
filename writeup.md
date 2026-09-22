# 📄 Agentic AI System - Technical Design Write-Up

## 1. Core Architecture & Design Decisions

### A. Autonomous Goal Decomposition & ReAct Loop
The system employs a **Plan-and-Solve / ReAct (Reason + Act)** architecture. When presented with a high-level natural language goal, the agent enters a **Planning Phase**, decomposing the objective into an ordered JSON array of sub-goals mapped directly to registered tools. This guarantees visual plan transparency before any execution occurs.

### B. Tool Orchestration Architecture
To prevent tight coupling, tools inherit from a uniform `BaseTool` interface defining standardized parameter schemas and returning `ToolResult` objects containing explicit `success`, `output`, `error`, and `metadata` attributes.
The system features **4 distinct operational tools**:
1. **`WebSearchTool`**: Live DuckDuckGo API query aggregator with HTTP HTML parsing fallback.
2. **`WebPageFetcherTool`**: HTML scraping and text content extraction engine.
3. **`CodeExecutorTool`**: Safe, isolated Python sandbox with stdout capturing for math, statistics, and data transformation.
4. **`FileReaderWriterTool`**: Local file workspace manager for persistent report generation.

### C. Self-Correction & Robustness Engine
Tool execution is monitored dynamically. If a tool fails (due to network timeout, HTTP 403, missing inputs, or execution exception):
1. The error is intercepted without terminating the process.
2. The agent increments an attempt counter and triggers a **Reflection & Re-planning Step**.
3. The LLM/Planner analyzes the failure traceback and dynamically reformulates the plan — either retrying with sanitized arguments or swapping to an alternative tool (e.g., swapping `web_search` for `code_executor` data extraction).
4. The system logs a structured **Self-Correction Event** in working memory.

### D. Provider Flexibility & Zero-Dependency Execution
To ensure out-of-the-box evaluation without mandatory external API keys, the framework supports standard LLMs (OpenAI, Gemini, Ollama) while providing a zero-dependency `HeuristicMockLLM` fallback.

---

## 2. System Limitations

1. **Sandboxed Code Execution Scope**:
   The `CodeExecutorTool` restricts execution to built-in mathematical functions, strings, data structures, and standard libraries (`math`, `json`). Advanced external Python libraries (`numpy`, `pandas`, `scipy`) are excluded to preserve execution safety.
2. **Sequential Step Execution**:
   Plan steps are executed sequentially rather than concurrently in parallel dependency graphs.
3. **Context Window Persistence**:
   Working memory tracks full step histories within single goal runs. Across separate CLI invocations, long-term state requires external persistent database integration.

---

## 3. Future Improvements (With More Time)

1. **DAG-Based Parallel Task Execution**:
   Upgrade the linear plan list to a Directed Acyclic Graph (DAG), enabling non-dependent sub-goals (e.g., simultaneous web searching and file fetching) to run in parallel via async event loops.
2. **Multi-Agent Collaboration Engine**:
   Split the single agent into specialized role agents (e.g., *Researcher Agent*, *Data Analyst Agent*, *Critic/Validator Agent*) communicating via a shared blackboard protocol.
3. **Docker/Wasm Code Isolation**:
   Containerize the `CodeExecutorTool` within ephemeral Docker or WebAssembly (Wasm) containers to safely support full `pandas` and `matplotlib` data visualization generation.
