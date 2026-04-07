import asyncio
import logging
from camel.agents import ChatAgent
from camel.toolkits import FileToolkit, SearchToolkit
from core.llm_config import get_llm_model
from core.utils import wrap_toolkit_with_exclusion
from core.settings import settings
from core.interpreter_tool import InterpreterToolkit
from agents.persona_setup import AUDITOR_SYS_MSG

logger = logging.getLogger("hacker-society")

class AuditorAgent:
    """
    Agentic auditor tasked with scanning code for vulnerabilities.
    Restored with high-fidelity observability and strict search filtering.
    """
    def __init__(self, loop: asyncio.AbstractEventLoop = None):
        self.model = get_llm_model()
        self.loop = loop or asyncio.get_event_loop()
        
        # 1. Strictly use target workspace from environment settings
        target_path = settings.TARGET_WORKSPACE_PATH
        
        # 2. Search Tools (Serper only)
        # Bypasses problematic serpapi schemas by filtering for 'serper'
        all_search_tools = SearchToolkit().get_tools()
        self.search_tools = []
        for t in all_search_tools:
            # Verified: uses 'openai_tool_schema' in this environment
            if hasattr(t, 'openai_tool_schema'):
                name = t.openai_tool_schema["function"]["name"]
                if "serper" in name.lower():
                    self.search_tools.append(t)
        
        # 3. High-Fidelity Interpreter (Custom Wrapper for mission telemetry)
        self.interpreter_toolkit = InterpreterToolkit(
            workspace_path=target_path, 
            loop=self.loop
        )
        
        # 4. Standard File Operations
        self.file_toolkit = FileToolkit(working_directory=target_path)
        
        # 5. Combined Workforce Tools
        # 'wrap_toolkit_with_exclusion' applies path safety, observability, and schema fixes
        self.tools = wrap_toolkit_with_exclusion([
            *self.file_toolkit.get_tools(),
            *self.interpreter_toolkit.get_tools(),
            *self.search_tools
        ])

        # 6. Build the underlying agent
        self.agent = ChatAgent(
            system_message=AUDITOR_SYS_MSG,
            model=self.model,
            tools=self.tools
        )
        
        logger.info(f"Auditor Agent realigned with 'openai_tool_schema' fix for {target_path}")
