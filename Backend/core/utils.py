import functools
from typing import List, Any
import logging
from camel.toolkits import FunctionTool
from core.websocket_manager import ws_manager
import asyncio

logger = logging.getLogger("hacker-society")

# Define global ignored patterns that cause token overflow or are irrelevant
IGNORED_PATTERNS = [
    ".venv",
    ".initial_env",
    ".venv_initial",
    "__pycache__",
    ".git",
    "node_modules",
    ".pytest_cache",
    ".vscode",
    ".idea",
    ".bak"
]

MAX_OUTPUT_LINES = 1000  # Safety limit to prevent context window overflow

def _wrap_tool_function(tool: FunctionTool, ignored_patterns: List[str], max_output_lines: int):
    """
    Factory function to create a wrapped tool function, avoiding the Python closure bug.
    Each tool function is captured in its own scope.
    """
    original_func = tool.func
    
    @functools.wraps(original_func)
    def wrapped_func(*args, **kwargs) -> Any:
        # 1. Path/Exclusion Check
        search_keys = ["path", "file_path", "pattern", "filepath", "dir_path", "file_paths"]
        
        for key in search_keys:
            val = kwargs.get(key)
            if val and isinstance(val, str):
                if any(p in val for p in ignored_patterns):
                    return f"Error: Access to '{val}' is restricted to preserve context window. Please focus on source code."
        
        # Position check for string arguments
        for arg in args:
            if isinstance(arg, str):
                if any(p in arg for p in ignored_patterns):
                    return f"Error: Access to '{arg}' is restricted to preserve context window. Please focus on source code."
        
        # 2. Execute original Tool
        result = original_func(*args, **kwargs)
        
        # 4. Streaming: Monitor for terminal/shell tools and broadcast raw output
        tool_name = getattr(tool, "tool_name", "").lower()
        is_terminal = any(term in tool_name for term in ["terminal", "shell", "exec", "run"])
        
        if is_terminal and ws_manager:
            try:
                # Clean the result for streaming (truncate if massive)
                display_result = str(result)[:2000] 
                # Use a fire-and-forget task to avoid blocking the main agent loop
                asyncio.create_task(ws_manager.broadcast_json("terminal_stream", {"output": display_result}))
            except Exception as stream_err:
                logger.error(f"Streaming error for {tool_name}: {stream_err}")

        # 3. Truncation/Context Optimization for large outputs
        if isinstance(result, str) and len(result.splitlines()) > max_output_lines:
            lines = result.splitlines()
            truncated_result = "\n".join(lines[:max_output_lines])
            footer = f"\n\n... [TRUNCATED {len(lines) - max_output_lines} LINES TO PRESERVE CONTEXT WINDOW] ..."
            return truncated_result + footer
            
        return result
    
    return wrapped_func

def wrap_toolkit_with_exclusion(tools: List[FunctionTool], ignored_patterns: List[str] = IGNORED_PATTERNS) -> List[FunctionTool]:
    """
    Wraps a list of CAMEL FunctionTools with a preemptive check for ignored path patterns.
    This version uses a factory function to correctly bind each tool's function.
    """
    wrapped_tools = []
    
    for tool in tools:
        # Wrap the function and replace it in the FunctionTool object
        tool.func = _wrap_tool_function(tool, ignored_patterns, MAX_OUTPUT_LINES)
        wrapped_tools.append(tool)
        
    return wrapped_tools
