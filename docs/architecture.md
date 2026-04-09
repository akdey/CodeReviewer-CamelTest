# Sentinel-Elite Architecture

Sentinel-Elite is an autonomous, multi-agent security workforce designed for end-to-end vulnerability research and remediation. It leverages the **CAMEL-AI** framework to coordinate specialized agents in a hierarchical structure.

## 🏗️ Workforce Hierarchy

The system operates using a **Strategist -> Worker** pattern, orchestrated by the `Workforce` and `Task` classes.

### 1. OWL Strategist (Coordinator)
The "Brain" of the operation.
- **Role**: Interprets high-level mission objectives, performs structural reconnaissance, and delegates specific sub-tasks to the Auditor and Fixer.
- **Capabilities**: Shell execution (`TerminalToolkit`), Web research (`SearchToolkit`), and visual walkthroughs (`BrowserToolkit`).

### 2. Security Auditor (Worker)
The "Hunter" of the operation.
- **Role**: Performs static and dynamic code analysis on the targeted codebase. 
- **Mission**: Identifies CVEs, secrets, and logical flaws. Its primary output is a `reproduction.py` script—a functional Proof-of-Concept (PoC).

### 3. SETA Fixer (Worker)
The "Engineer" of the operation.
- **Role**: Remediation and verification.
- **Mission**: Analyzes the Auditor's reproduction script, applies a source-code patch, and re-runs the PoC to verify that the vulnerability is neutralized.

## 🔄 Mission Lifecycle

1.  **Phase 1: Intelligence Recon**: The Structural Architect scans the target codebase to generate architecture maps.
2.  **Phase 2: Strategy Drafting**: The OWL Strategist consumes the recon data and formulates an audit plan.
3.  **Phase 3: Execution Loop**:
    -   Auditor scans and reproduces vulnerabilities.
    -   Fixer patches and verifies.
4.  **Phase 4: Synthesis**: The workforce generates a final mission report in the `report/` folder.

## 🛠️ Internal Bridges

- **Telemetry Gateway**: All tools are wrapped by a unified utility that captures raw I/O and streams it to the frontend via WebSockets.
- **Persistent Skill Bank**: Remediation logic and scripts generated during missions are saved to the `skills/` folder for reuse in future missions.
