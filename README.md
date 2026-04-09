# 🦉 Sentinel-Elite: Autonomous Security Workforce

### *Harnessing Agentic Swarms for Structural Cyber-Research*

**Sentinel-Elite** is a premium, "Glass-Box" simulation platform built on the **CAMEL-AI** framework. It orchestrates a specialized workforce of autonomous security agents that collaborate to map, audit, and remediate complex codebases with total transparency.

---

## 🚀 Architectural Pillars

Sentinel-Elite moves beyond simple "chat bots" by implementing a hierarchical task-solving architecture:

- **CodeRecon Phase**: Autonomous structural analysis to map project architecture before any audit begins.
- **Glass-Box Telemetry**: Real-time streaming of raw terminal commands, browser actions, and "neural" agent reasoning.
- **Library-First Integration**: Powered by native CAMEL-AI toolkits for high-performance, scoped execution.
- **Optimized Context**: 150k token windows with automatic memory pruning for enterprise-scale repositories.

---

## 🛠️ The Specialized Workforce

| Agent | Designation | Core Mission |
| :--- | :--- | :--- |
| **OWL Strategist** | `Coordinator` | Decomposes mission goals, manages tool permissions, and routes intelligence. |
| **Security Auditor** | `Hunter` | Identifies logical flaws and generates functional Proof-of-Concept (PoC) scripts. |
| **SETA Fixer** | `Engineer` | Performs source-level patching and re-validates the environment against PoCs. |

---

## 📡 Features & Observability

- **Neural Feed**: Real-time broadcast of inter-agent coordination and tool-use rationale.
- **Tactical Terminal**: Raw `stdout` pipe showing exactly what the agents are executing in the shell.
- **Structural Briefing**: Automated generation of `architecture.md` and `module-analysis.md` for target projects.
- **Skill Persistence**: Security scripts and remediation logic are saved for reuse across missions.

---

## 📦 Project Structure

```text
.
├── Backend/                 # CAMEL-AI Engine & Telemetry Gateway
├── docs/                    # Technical deep-dives (Architecture, Recon, Memory)
├── frontend/                # Sentinel Dashboard (Next.js/Xterm.js)
└── targeted_source_code/    # The target repository under research
```

---

## 🚦 Quick Start

### 1. Prerequisites
- Python 3.11+
- `uv` package manager (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Node.js & npm (for the Dashboard)

### 2. Deployment
```bash
# Clone and setup backend
cd Backend
uv sync
uv run fastapi run

# Start the Dashboard
cd ../frontend
npm install
npm run dev
```

### 3. Initialize Mission
Access the Dashboard at `http://localhost:5173`. Select your target path and trigger the **Structural Recon** phase to begin the mission.

---

## 📚 Technical Documentation

For in-depth analysis of the platform's internal mechanics, please refer to the documentation suite:

*   [**Architecture & Hierarchy**](docs/architecture.md)
*   [**Structural Recon Service**](docs/recon_service.md)
*   [**Glass-Box Telemetry Protocol**](docs/observability.md)
*   [**Context & Memory Management**](docs/context_management.md)

---

> [!IMPORTANT]
> **Sentinel-Elite** is designed for authorized security research only. All agents are strictly scoped to the `TARGET_WORKSPACE_PATH` to ensure host system safety.
