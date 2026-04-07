import asyncio
import logging
import os
from typing import Any, List, Optional
from camel.interpreters import SubprocessInterpreter
from camel.toolkits import FunctionTool
from core.websocket_manager import ws_manager

logger = logging.getLogger("hacker-society")

class InterpreterToolkit:
    """
    A persistent, high-fidelity terminal wrapper for the Sovereign IDE.
    Provides real-time mission telemetry and strict workspace isolation.
    """
    
    def __init__(self, workspace_path: str, loop: asyncio.AbstractEventLoop):
        self.workspace_path = workspace_path
        self._loop = loop
        # Initialize SubprocessInterpreter with confirmation disabled
        self.interpreter = SubprocessInterpreter(
            require_confirm=False,
            print_stdout=False, # Managed via WebSocket streaming
            print_stderr=True,
            execution_timeout=300 # Deep security audits can be long
        )

    def run_shell_command(self, command: str) -> str:
        """
        Executes a shell command in the context of the project workspace.
        Broadcasts the live output to the dashboard for transparent 'Glass Box' observability.
        
        Args:
            command (str): The shell command to execute.
            
        Returns:
            str: The final combined output of the command.
        """
        # Strictly lock execution to the project directory
        workspace_command = f"cd {self.workspace_path} && {command}"
        
        logger.info(f"Executing workspace command: {command}")
        
        # Immediate notification to UI about command initiation
        ws_manager.emit("terminal_stream", {
            "command": command,
            "output": f"Executing in {self.workspace_path}:\n$ {command}\n"
        })
        
        try:
            # Execute the command via CAMEL logic
            result = self.interpreter.execute_command(workspace_command)
            
            # Post-execution full result push
            ws_manager.emit("terminal_stream", {
                "command": command,
                "output": result
            })
            
            return result
            
        except Exception as e:
            error_msg = f"Interpreter execution failed: {str(e)}"
            logger.error(error_msg)
            ws_manager.emit("terminal_stream", {
                "command": command,
                "output": f"\n[ERROR]: {error_msg}\n"
            })
            return error_msg

    def get_tools(self) -> List[FunctionTool]:
        """
        Returns the terminal tools to be registered with the agent workforce.
        """
        return [
            FunctionTool(self.run_shell_command)
        ]
