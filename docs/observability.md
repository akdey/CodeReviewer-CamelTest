# Feature: Glass-Box Observability

Sentinel-Elite is designed to be fully transparent. The project implements a **"Glass-Box"** philosophy, ensuring every agent thought and tool execution is observable in real-time.

## 📡 Unified Telemetry Gateway

Central to our observability is the `wrap_toolkit_with_exclusion` utility in `Backend/core/utils.py`. This high-order function wraps every tool in the workforce and intercepts execution data.

### Supported Streams
- **Tactical Terminal**: Captures raw `stdout` and `stderr` from the `TerminalToolkit`.
- **Visual Browser Feed**: Captures screenshots and action summaries from the `BrowserToolkit`.
- **Neural Feed**: Captures internal agent "thoughts" and reasoning chains.

## 🧵 Real-time WebSocket Protocol

All telemetry is broadcast over a multiplexed WebSocket connection (`/ws/communications`).

| Channel | Data Type | Visualization |
| :--- | :--- | :--- |
| `thought_stream` | Agent reasoning strings | Side-panel dialogue bubbles |
| `terminal_stream` | Shell commands & raw output | Interactive Xterm.js console |
| `diff_stream` | Code patches (Unified Diffs) | Parallel code differentiator |
| `system` | Mission status & phase updates | Central notification log |

## 🛡️ Path Security & Filtering

The observability layer also acts as a safety barrier. When a tool is called, the telemetry wrapper checks the target path against `IGNORED_PATTERNS`.

**Blocked paths include:**
- `.venv/` (Prevention of environment poisoning)
- `.git/` (Prevention of history manipulation)
- `.env` (Prevention of credential leaking)

This ensures the user can watch the mission unfold in a safe, sandboxed visualization without risking the host environment.
