import asyncio
import os
from camel.agents import ChatAgent
from camel.messages import BaseMessage

# Import REAL tools from CAMEL-AI natively
from camel.toolkits import TerminalToolkit, FileToolkit 

from core.settings import settings
from core.llm_config import get_llm_model
from core.websocket_manager import ws_manager
from core.utils import wrap_toolkit_with_exclusion
from agents.persona_setup import FIXER_SYS_MSG

class FixerAgent:
    def __init__(self):
        self.model = get_llm_model()
        
        # Use target workspace defined or default fallback directly adjacent
        target_path = getattr(settings, "TARGET_WORKSPACE_PATH", os.path.join(os.getcwd(), "../targeted_source_code"))
        
        # REAL tools binding!
        self.terminal_toolkit = TerminalToolkit(working_directory=target_path)
        self.file_toolkit = FileToolkit(working_directory=target_path)
        
        # Apply the exclusion filter and output truncation to file tools
        tools = [
            *self.terminal_toolkit.get_tools(),
            *wrap_toolkit_with_exclusion(self.file_toolkit.get_tools())
        ]
        
        self.agent = ChatAgent(
            system_message=FIXER_SYS_MSG,
            model=self.model,
            tools=tools,
        )

    async def execute_patch_loop(self, task_instruction: str):
        """
        Executes a patching loop with validation.
        """
        user_msg = BaseMessage.make_user_message(role_name="User", content=task_instruction)
        
        await ws_manager.broadcast_json("thought_stream", {
            "agent": "SETA Fixer",
            "message": f"Starting patch operations for directive: {task_instruction}"
        })

        # We step the agent. It has the physical tools to run pip/uv, and rewrite app.py
        response = self.agent.step(user_msg)
        
        await ws_manager.broadcast_json("thought_stream", {
            "agent": "SETA Fixer",
            "message": response.msg.content
        })

        return response.msg.content
