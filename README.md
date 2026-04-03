# 🕶️ Camel-Reviewer: Agentic Code Auditor

### *Autonomous Cybersecurity Research & Orchestration Framework*

**Camel-Reviewer** is a next-generation "Glass Box" simulation environment built on the **CAMEL-AI** multi-agent framework. It provides a transparent, real-time visualization of autonomous agents (Auditors, Fixers, Strategists) as they perform vulnerability research, reconnaissance, and automated patching against target environments.

---

## 🚀 The Vision: "Glass Box" Transparency

Most multi-agent systems operate as "Black Boxes"—tokens go in, results come out. **Camel-Reviewer** leverages the **OWL (Open World Learning)** and **SETA (Symbolic Evaluation & Transformation of Agents)** concepts to provide:
- **Mission Blueprint**: Live visualization of task decomposition and job segregation.
- **Neural Feed**: Real-time streaming of agent thoughts, tool-use rationale, and inter-agent coordination.
- **Execution Loop**: Step-by-step breadcrumbs showing the progression from strategy to exploitation to defense.

---

## 🛠️ Technology Stack

| Layer | Technology |
| :--- | :--- |
| **Core AI Engine** | [CAMEL-AI](https://www.camel-ai.org/) (Workforce, RolePlayingWorker, Toolkit) |
| **Backend API** | FastAPI (Python 3.11+) |
| **Orchestration** | OWL Strategist & SETA-inspired Task Assignment |
| **Frontend** | React (Vite) + Lucide Icons + Xterm.js |
| **Real-time I/O** | WebSockets (Multiplexed Streams) |

---

## 🧱 Tool Implementation Details

**Camel-Reviewer** implements advanced agentic toolkits to empower the Hacker Society:

### 1. FileSystem & Shell Toolkit
- **Mechanism**: Utilizes native **Subprocess** and **Git** bindings to interact with targeted repositories.
- **Capabilities**: Allows the `FixerAgent` to perform recursive file reads, symbolic code analysis, and automated pull-request-style patching.
- **Implementation**: See [docs/walkthrough.md](docs/walkthrough.md) for module mappings.

### 2. WebSearch Toolkit
- **Mechanism**: Powered by the **DuckDuckGo Search** toolkit (`duckduckgo-search`).
- **Capabilities**: Enables real-time gathering of CVE details, threat intelligence, and exploit research without requiring expensive API keys.

---

## 📦 Project Structure

```text
.
├── Backend/          # FastAPI Engine & Agent Logic
├── docs/             # Consolidated Implementation Documentation
├── frontend/         # React Dashboard (Camel-Reviewer Hub)
└── targeted_source_code/ # The "Victim" codebase for simulations
```

---

## 🚦 Getting Started

### 1. Requirements
- Python 3.11+
- `uv` installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Node.js (for frontend)

### 2. Environment Setup
Create a `.env` in the `Backend/` directory:
```env
GROQ_API_KEY=your_key_here
ACTIVE_PROVIDER=groq
TARGET_WORKSPACE_PATH=/absolute/path/to/targeted_source_code
```

---

## 🔍 Core Features
- **Mission Blueprint**: Visualizes the hierarchical decomposition of complex audit goals.
- **Agent Neural Feed**: Filters and streams raw agent dialogue and system-level coordination.
- **Code Differentiator**: Automatically captures and highlights file changes made by the FixerAgent.
- **Terminal I/O**: Real-time pipe of the agent's shell interactions and tool executions.

---

## 🗺️ Roadmap: Scaling to Enterprise Codebases

Today, **Camel-Reviewer** operates in **Direct Analysis Mode**, where agents read "whole files" (e.g., `pyproject.toml`, `app.py`) for vulnerability identification. For massive repositories, we are evolving towards:

### 1. RAG-based Context Injection (Retrieval-Augmented Generation)
- **Problem**: Large codebases exceed LLM context windows and result in high token costs.
- **Solution**: Index the repository into a vector database (ChromaDB/Weaviate).
- **Execution**: Agents will use **Semantic Search Tools** to query relevant code snippets across thousands of files, only pulling what's necessary into the "Glass Box".

### 2. SETA-Driven Task Slicing
- **Evolution**: Using **Symbolic Evaluation (SETA)** to automatically slice a massive audit into symbolic chunks, parallelizing the audit across a "Swarm" of specialized workers.

---

## 📄 Documentation
For a deep dive into the code architecture, module mappings, and future SETA roadmap, see:
[**Implementation Walkthrough & Future Scope**](docs/walkthrough.md)
