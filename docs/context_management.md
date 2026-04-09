# Feature: Context & Memory Management

Sentinel-Elite is optimized for long-running, complex security missions that generate massive amounts of log data and source code analysis.

## 🧠 High-Context Capacity

All agents in the workforce are configured with a **150,000 token limit**. This is designed to leverage high-context Large Language Models (LLMs) like Gemini 1.5.

### Benefits
- **Deep Recall**: The Auditor can "remember" structural insights from the initialization phase throughout the entire mission.
- **Large Dumps**: The system can handle raw 10,000-character terminal outputs without truncating the "thought stream."

## 🧹 Automatic Memory Pruning

To maintain performance over missions that may span hours, we implement **Automatic Memory Pruning** (`prune_tool_calls_from_memory=True`).

### How it Works
1.  **Execution**: An agent calls a tool (e.g., `TerminalToolkit.shell_exec`).
2.  **Consumption**: The tool output is fed to the agent.
3.  **Purge**: Once the agent has generated a response based on the tool result, the raw result is cleared from its short-term memory history while the *conclusions* are kept.
4.  **Result**: This significantly reduces token overhead and prevents "context bloat" from redundant terminal dumps.

## ⚖️ Summarization Strategy

We use a **Summarize Threshold of 80%**.

- **Phase 1 (High Fidelity)**: Under 80% utilization (120k tokens), the agent preserves every line of reasoning.
- **Phase 2 (Compression)**: Once usage crosses 80%, the agent automatically triggers a CAMEL summarization task to compress historical context into a dense state representation, freeing up space for new mission steps.

This tiered approach ensures that critical security details aren't lost to "noise" during high-activity missions.
