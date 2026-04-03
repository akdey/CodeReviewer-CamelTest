# 🧩 Implementation Walkthrough: ACRO: Agentic Cyber-Orchestration

This document provides a deep dive into the architecture, module design, and integration logic of the **ACRO** framework.

---

### 🕵️ Verified Audit Results
Agents have successfully analyzed the `targeted_source_code` using the **ACRO** framework and identified critical vulnerabilities:
- **Unauthenticated Routes**: Discovered API endpoints that were accessible without session tokens.
- **Logic Flaws**: Identified missing validation in the authentication middleware logic.

---

## 🏛️ System Architecture

The project follows a **Multiplexed Agent-to-UI** architecture:

1.  **FastAPI (Main Loop)**: Manages persistence, WebSocket heartbeats, and lifecycle events.
2.  **CAMEL Workforce (Background Process)**: Executes the non-deterministic mission loop.
3.  **WebSocket Manager**: A thread-safe bridge that routes internal agent events back to the React UI using `asyncio.run_coroutine_threadsafe`.

---

## 🏗️ Toolkit Implementation Mechanics

**ACRO** empowers agents with specialized toolsets to perform autonomous audits:

### 1. FileSystem & Shell (Subprocess)
- **Module**: Handled via custom agent-level tool registration.
- **Implementation**: The `FixerAgent` executes shell commands and Git operations through a protected `Subprocess` interface. This allows the agent to:
    - `ls -R`: Recursively map the codebase.
    - `cat`: Read source files for vulnerability identification.
    - `git checkout -b fix`: Branch the repository for safe patching.
- **Observation**: Real-time results are piped to the **Terminal I/O** panel in the dashboard.

### 2. WebSearch (DuckDuckGo)
- **Module**: `auditor_agent.py` using `camel.toolkits.search_toolkit.SearchToolkit`.
- **Implementation**: Leverages the **DuckDuckGo Search** backend to perform real-time, zero-cost intelligence gathering.
- **Use Case**: The `AuditorAgent` uses this to research unknown library vulnerabilities or download exploit PoCs to verify findings.

---

## 📦 Module Walkthrough & CAMEL Integration

### 1. `Backend/agents/society.py` (The Orchestra)
- **Functions Used**: `camel.societies.workforce.Workforce`, `camel.societies.workforce.RolePlayingWorker`.
- **Purpose**: Defines the workers (Auditor, Fixer) and the Coordinator (Strategist). It initializes the mission and manages the top-level task assignment.
- **OWL Integration**: Uses the **OWL Strategist** persona to handle task decomposition logic before dispatching to workers.

### 2. `Backend/core/workforce_tracking.py` (The Nervous System)
- **Functions Used**: `camel.societies.workforce.workforce_callback.WorkforceCallback`.
- **Purpose**: A native implementation of the CAMEL callback interface. It "taps" into the workforce's internal events (`task_decomposed`, `task_assigned`, `log_message`) and broadcasts them to the UI as structured JSON.
- **Rationale Capture**: Explicitly searches for strategy/decomposition logs to surface the **basis** for job segregation.

---

## 🔮 Future Scope & Roadmaps

### A. Core Evolution
1.  **Multi-Model Debate**: Integrating **OWL** thinkers to debate a vulnerability before the Auditor confirms it.
2.  **Long-term Memory (RAG)**: Allowing the society to "remember" successful patch patterns across different mission runs.

### B. OWL & SETA Roadmap
- **OWL (Open World Learning)**:
    - **Recursive Skill Learning**: Agents should use their own `FixerAgent` to write custom tools for themselves when a mission requires a tool that isn't in their current toolkit.
- **SETA (Symbolic Evaluation & Transformation of Agents)**:
    - **Dynamic Workforce Reshaping**: If the Auditor finds too many vulnerabilities, SETA should automatically spawn *multiple* FixerAgents and transform the linear sequence into a parallel "Swarm" of patchers.

---

## 📄 References
- [Features Analysis](features_analysis.md)
- [Project Vision](../README.md)
