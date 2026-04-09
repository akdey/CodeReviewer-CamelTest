import asyncio
import logging
from camel.agents import ChatAgent
from camel.toolkits import (
    FileToolkit, 
    SearchToolkit, 
    CodeExecutionToolkit,
    SkillToolkit,
    BrowserToolkit,
    TerminalToolkit
)
from core.llm_config import get_llm_model
from core.utils import wrap_toolkit_with_exclusion
from core.observed_agent import ObservedChatAgent
from core.settings import settings
from agents.persona_setup import FIXER_SYS_MSG

logger = logging.getLogger("hacker-society")

class FixerAgent:
    """
    Agentic fixer tasked with remediating vulnerabilities.
    Enriched with Sentinel-Elite verification tools: Code Execution, Skill Bank, and Browser.
    """
    def __init__(self, loop: asyncio.AbstractEventLoop = None):
        self.model = get_llm_model()
        self.loop = loop or asyncio.get_event_loop()
        
        target_path = settings.TARGET_WORKSPACE_PATH
        
        # 1. Search Tools (Serper only)
        all_search_tools = SearchToolkit().get_tools()
        self.search_tools = []
        for t in all_search_tools:
            if hasattr(t, 'openai_tool_schema'):
                name = t.openai_tool_schema["function"]["name"]
                if "serper" in name.lower():
                    self.search_tools.append(t)
        
        # 2. Sentinel-Elite Toolkits
        self.code_exec_toolkit = CodeExecutionToolkit(sandbox="subprocess")
        self.skill_toolkit = SkillToolkit(working_directory="skills/")
        self.browser_toolkit = BrowserToolkit(headless=False)
        self.terminal_toolkit = TerminalToolkit(working_directory=target_path)
        self.file_toolkit = FileToolkit(working_directory=target_path)
        
        # 3. Combined Workforce Tools
        self.tools = wrap_toolkit_with_exclusion([
            *self.file_toolkit.get_tools(),
            *self.terminal_toolkit.get_tools(),
            *self.browser_toolkit.get_tools(),
            *self.code_exec_toolkit.get_tools(),
            *self.skill_toolkit.get_tools(),
            *self.search_tools
        ])

        # 5. Build the underlying agent
        self.agent = ObservedChatAgent(
            system_message=FIXER_SYS_MSG,
            model=self.model,
            tools=self.tools,
            agent_name="SETA Fixer",
            loop=self.loop,
            token_limit=200000,
            summarize_threshold=80,
            prune_tool_calls_from_memory=True
        )
        
        logger.info(f"Fixer Agent upgraded to Sentinel-Elite for {target_path}")
