import os
import zipfile
import shutil
import logging
import functools
import asyncio
import json
from typing import Any, List, Dict
from git import Repo
import aiofiles
from core.settings import settings
from core.websocket_manager import ws_manager
from camel.toolkits import FunctionTool

logger = logging.getLogger("hacker-society")

# Strictly ignored patterns per user directive
IGNORED_PATTERNS = [
    ".git",
    ".initial_env",
    ".venv",
    "__pycache__",
    ".pytest_cache"
]

def extract_zip(zip_path: str, extract_to: str):
    """
    Safely extracts a ZIP archive and ensures the target directory is clean.
    """
    if os.path.exists(extract_to):
        logger.info(f"Cleaning existing workspace at {extract_to}...")
        # Use shutil.rmtree for robust directory removal
        try:
            shutil.rmtree(extract_to)
        except Exception as e:
            logger.error(f"Cleanup error in workspace extraction: {e}")
            
    os.makedirs(extract_to, exist_ok=True)
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    logger.info(f"ZIP extracted to {extract_to}")

def clone_git_repo(repo_url: str, target_path: str):
    """
    Clones a remote Git repository into the target workspace.
    """
    if os.path.exists(target_path):
        logger.info(f"Cleaning existing workspace at {target_path}...")
        try:
            shutil.rmtree(target_path)
        except Exception as e:
            logger.error(f"Cleanup error in git cloning: {e}")
    
    logger.info(f"Cloning {repo_url} into {target_path}...")
    Repo.clone_from(repo_url, target_path)
    logger.info("Clone complete.")

def fix_tool_schema(schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively injects 'additionalProperties': False into tool schemas to satisfy 
    strict LLM validation requirements. 
    Handles anyOf, allOf, oneOf, array items, and implicit objects.
    """
    if not isinstance(schema, dict):
        return schema
    
    schema = schema.copy()
    
    # If it has properties or is type object, it must have additionalProperties: False
    if schema.get("type") == "object" or "properties" in schema:
        if schema.get("additionalProperties") is not False:
            schema["additionalProperties"] = False
            
    # Recurse into properties
    if "properties" in schema:
        new_props = {}
        for prop_name, prop_val in schema["properties"].items():
            new_props[prop_name] = fix_tool_schema(prop_val)
        schema["properties"] = new_props
            
    # Handle combined schemas (anyOf, allOf, oneOf)
    for key in ["anyOf", "allOf", "oneOf"]:
        if key in schema and isinstance(schema[key], list):
            schema[key] = [fix_tool_schema(s) for s in schema[key]]
            
    # Handle array items
    if schema.get("type") == "array" and "items" in schema:
        schema["items"] = fix_tool_schema(schema["items"])
            
    return schema

def _create_safe_tool_wrapper(original_func):
    """
    A factory function to correctly capture original_func in a closure,
    preventing tool-calling cross-talk and argument mismatch errors.
    """
    @functools.wraps(original_func)
    def safe_wrapper(*args, **kwargs):
        # 1. Path Safety Check
        all_path_candidates = list(args) + list(kwargs.values())
        for candidate in all_path_candidates:
            if isinstance(candidate, str):
                if any(p in candidate for p in IGNORED_PATTERNS):
                    logger.warning(f"Blocked access to restricted path: {candidate}")
                    return f"Error: Access to '{candidate}' is restricted to protect system integrity."

        # 2. Execute original tool logic
        try:
            result = original_func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Tool execution failed in safe_wrapper [{original_func.__name__}]: {e}")
            return f"Tool execution failed: {str(e)}"

        # 3. Terminal Observability
        # Distinguish shell commands for dashboard streaming
        func_name = original_func.__name__.lower()
        is_shell = any(term in func_name for term in ["terminal", "shell", "exec", "run_command"])
        
        if is_shell:
            command = kwargs.get("command") or (args[0] if args and isinstance(args[0], str) else "cli-command")
            ws_manager.emit("terminal_stream", {
                "command": str(command),
                "output": str(result)[:3000] # Truncate massive outputs
            })
            
        return result
        
    return safe_wrapper

def wrap_toolkit_with_exclusion(tools: List[Any]) -> List[Any]:
    """
    Unified entrypoint for securing and observing a list of agent tools.
    Corrects openai_tool_schema to eliminate Azure/OpenAI 400 validation errors.
    """
    for tool in tools:
        # Wrap the function logic using the factory function to preserve closures
        tool.func = _create_safe_tool_wrapper(tool.func)
        
        # Stabilize JSON schema for strict Azure/OpenAI validation
        # verified: uses 'openai_tool_schema' in this environment
        if hasattr(tool, 'openai_tool_schema'):
            # The schema is stored in tool.openai_tool_schema['function']['parameters']
            if "function" in tool.openai_tool_schema and "parameters" in tool.openai_tool_schema["function"]:
                tool.openai_tool_schema["function"]["parameters"] = fix_tool_schema(
                    tool.openai_tool_schema["function"]["parameters"]
                )
            
    return tools

def observe_toolkit():
    """
    DEPRECATED: Provided for backwards compatibility.
    """
    return lambda x: x
