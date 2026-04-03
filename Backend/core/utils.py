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

def wrap_toolkit_with_exclusion(tools: List[FunctionTool], ignored_patterns: List[str] = IGNORED_PATTERNS) -> List[FunctionTool]:
    """
    Wraps a list of CAMEL FunctionTools with a preemptive check for ignored path patterns.
    If a tool argument (path, pattern, or file_path) matches an ignored pattern,
    the tool returns a restricted access message instead of executing.
    """
    filtered_tools = []
    
    for tool in tools:
        original_func = tool.func
        
        @functools.wraps(original_func)
        def wrapped_func(*args, **kwargs) -> Any:
            # Check all string/path arguments for ignored patterns
            # We look for common argument names used in FileToolkit
            search_keys = ["path", "file_path", "pattern", "filepath", "dir_path"]
            
            for key in search_keys:
                val = kwargs.get(key)
                if val and isinstance(val, str):
                    if any(p in val for p in ignored_patterns):
                        return f"Error: Access to '{val}' is restricted to preserve context window. Please focus on source code."
            
            # Also check positional args if any (though CAMEL usually uses kwargs)
            for arg in args:
                if isinstance(arg, str):
                    if any(p in arg for p in ignored_patterns):
                        return f"Error: Access to '{arg}' is restricted to preserve context window. Please focus on source code."
            
            return original_func(*args, **kwargs)
        
        # Replace the function in the FunctionTool object
        tool.func = wrapped_func
        filtered_tools.append(tool)
        
    return filtered_tools
