import functools
from typing import List, Any
from camel.toolkits import FunctionTool

# Define global ignored patterns that cause token overflow or are irrelevant
IGNORED_PATTERNS = [
    ".venv",
    ".initial_env",
    "__pycache__",
    ".git",
    "node_modules",
    ".pytest_cache",
    ".vscode",
    ".idea"
]

MAX_OUTPUT_LINES = 1000  # Safety limit to prevent context window overflow

def wrap_toolkit_with_exclusion(tools: List[FunctionTool], ignored_patterns: List[str] = IGNORED_PATTERNS) -> List[FunctionTool]:
    """
    Wraps a list of CAMEL FunctionTools with a preemptive check for ignored path patterns.
    Also implements output truncation for file reading operations to save tokens.
    """
    filtered_tools = []
    
    for tool in tools:
        original_func = tool.func
        
        @functools.wraps(original_func)
        def wrapped_func(*args, **kwargs) -> Any:
            # 1. Path/Exclusion Check
            search_keys = ["path", "file_path", "pattern", "filepath", "dir_path"]
            
            for key in search_keys:
                val = kwargs.get(key)
                if val and isinstance(val, str):
                    if any(p in val for p in ignored_patterns):
                        return f"Error: Access to '{val}' is restricted to preserve context window. Please focus on source code."
            
            # Position check
            for arg in args:
                if isinstance(arg, str):
                    if any(p in arg for p in ignored_patterns):
                        return f"Error: Access to '{arg}' is restricted to preserve context window. Please focus on source code."
            
            # 2. Execute original Tool
            result = original_func(*args, **kwargs)
            
            # 3. Truncation/Context Optimization for large outputs
            # Only truncate string results (likely from read_file or search_files)
            if isinstance(result, str) and len(result.splitlines()) > MAX_OUTPUT_LINES:
                lines = result.splitlines()
                truncated_result = "\n".join(lines[:MAX_OUTPUT_LINES])
                footer = f"\n\n... [TRUNCATED {len(lines) - MAX_OUTPUT_LINES} LINES TO PRESERVE CONTEXT WINDOW] ..."
                return truncated_result + footer
                
            return result
        
        # Replace the function in the FunctionTool object
        tool.func = wrapped_func
        filtered_tools.append(tool)
        
    return filtered_tools
