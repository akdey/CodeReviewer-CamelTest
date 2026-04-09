import asyncio
import logging
from camel.agents import ChatAgent
from camel.toolkits import FileToolkit
from core.llm_config import get_llm_model
from core.utils import wrap_toolkit_with_exclusion
from core.observed_agent import ObservedChatAgent
from core.custom_tools import semantic_code_search
from core.settings import settings
from agents.persona_setup import ARCHITECT_SYS_MSG

logger = logging.getLogger("hacker-society")

class StructuralArchitectAgent:
    """
    Agentic architect tasked with codebase cartography.
    Uses FileToolkit to scan and Source2Synth principles to document.
    """
    def __init__(self, loop: asyncio.AbstractEventLoop = None):
        self.model = get_llm_model()
        self.loop = loop or asyncio.get_event_loop()
        
        target_path = settings.TARGET_WORKSPACE_PATH
        
        # 1. Native File Operations
        self.file_toolkit = FileToolkit(working_directory=target_path)
        
        # 2. Combined Tools
        # wrap_toolkit_with_exclusion handles safety and telemetry
        self.tools = wrap_toolkit_with_exclusion([
            *self.file_toolkit.get_tools(),
            semantic_code_search
        ])

        # 3. Build the underlying agent
        self.agent = ObservedChatAgent(
            system_message=ARCHITECT_SYS_MSG,
            model=self.model,
            tools=self.tools,
            agent_name="Structural Architect",
            loop=self.loop
        )
        
        logger.info(f"Structural Architect Agent initialized for {target_path}")
