# Sentinel-Elite Security Workforce: Feature Guide

Sentinel-Elite is an autonomous, agentic security framework built on the CAMEL-AI ecosystem. It is designed to perform deep vulnerability research, secret hunting, and automated remediation with professional-grade reporting and observability.

## 🚀 Core Capabilities

### 1. Autonomous Security Workforce
- **OWL Strategist**: A high-reasoning coordinator that breaks down security missions into tactical tasks.
- **Auditor Agent**: Specialized in static and dynamic analysis, secret hunting, and vulnerability verification.
- **Fixer Agent**: Responsible for applying patches and verifying fixes through automated testing.

### 2. Sentinel-Elite Toolkits
Equipped with a suite of "Glass-Box" toolkits for maximum operational efficiency:
- **TerminalToolkit**: Full shell access within a secured workspace environment.
- **FileToolkit**: Precise file manipulation using native CAMEL editing logic (Strictly "No-Sed").
- **BrowserToolkit**: Visible browser automation for deep research and CVE verification.
- **CodeExecutionToolkit**: Subprocess-based sandboxing for PoC verification.
- **ExcelToolkit**: Automated generation of professional CVE dashboards in `report/`.

### 3. Mission Artifact Management
All mission-critical data is strictly centralized to prevent codebase pollution:
- **`report/`**: Centralized hub for Excel dashboards, markdown summaries, and test results.
- **`.sentinel_repro/`**: A hidden directory for ephemeral reproduction scripts and PoCs.
- **`skills/`**: A persistent bank of learned security maneuvers and reusable scripts.

### 4. Safety & Stability Features
- **Strict Path Isolation**: Agents are restricted to the `TARGET_WORKSPACE_PATH`, preventing accidental host system modifications.
- **Massive Repo Truncation**: A specialized safety layer in `core/utils.py` prevents "Summarization Loops" by capping tool outputs at 50,000 characters.
- **Authentication Hardening**: Explicit LLM validation and logging prevent 401 errors and ensure mission continuity.

### 5. Glass-Box Observability
Real-time telemetry is streamed via WebSockets to the frontend dashboard:
- **Neural Feed**: Live stream of agent reasoning and tool usage.
- **Terminal Stream**: Real-time visibility into shell commands and outputs.
- **Tactical Highlights**: Visual notifications of browser actions and high-priority findings.

## 🛠 Usage
To initiate a full security mission, trigger the `/api/start_audit` endpoint with the target repository details. The workforce will autonomously:
1. **Index** the codebase.
2. **Scan** for secrets and vulnerabilities.
3. **Generate** an Excel CVE dashboard.
4. **Develop** patches for identified issues.
5. **Verify** fixes with `pytest`.
6. **Move** all artifacts to the `report/` directory.

---
*Sentinel-Elite: The autonomous guard for the future of code.*
