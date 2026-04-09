# Feature: Structural Reconnaissance Service

The **CodeReconService** is a mission-critical component that provides the workforce with deep architectural context before any security auditing begins.

## 🎯 Objectives

Most security scanners struggle with "forest for the trees" syndrome—finding a single line bug but missing a massive architectural flaw. The Recon Service fixes this by:
1.  **Mapping Entry Points**: Identifying where the app receives input (API routes, CLI flags).
2.  **Structural Analysis**: Documenting how files relate to each other.
3.  **Synthesis**: Creating a human-readable "Intelligence Briefing" for the agents.

## 🛠️ Implementation

The service orchestrates a specialized **Structural Architect Agent** using:

- **Source2Synth**: A native CAMEL capability that synthesizes raw code into structured Q&A and documentation.
- **Project Walkthrough**: The architect uses `FileToolkit` to recursively list and summarize all active modules.

### Output Artifacts
The service generates the following in the `report/` folder of the target workspace:
- `architecture.md`: A high-level view of the project's logic flow.
- `module-analysis.md`: A file-by-file breakdown of key dependencies and sensitive areas.

## 🧠 Intelligence Injection

Once the documentation is generated, the `CodeReconService` extracts the key findings and injects them into the **OWL Strategist's** global task.

**Example Injection:**
> "MISSION INTEL: The target is a FastAPI application. Core auth logic is in `auth/security.py`. All unauthenticated routes are handled by the `router_public` group."

This ensures the **Security Auditor** starts its scan with a "warm" understanding of where vulnerabilities are most likely to exist.
