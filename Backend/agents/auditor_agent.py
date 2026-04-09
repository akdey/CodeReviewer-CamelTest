import os
import asyncio
import logging
from camel.agents import ChatAgent
from camel.toolkits import (
    FileToolkit, 
    SearchToolkit, 
    ExcelToolkit, 
    BrowserToolkit, 
    CodeExecutionToolkit,
    SkillToolkit,
    TerminalToolkit
)
from core.llm_config import get_llm_model
from core.utils import wrap_toolkit_with_exclusion
from core.settings import settings
from agents.persona_setup import AUDITOR_SYS_MSG

logger = logging.getLogger("hacker-society")

class AuditorAgent:
    """
    Agentic auditor tasked with scanning code for vulnerabilities.
    Enriched with Sentinel-Elite capabilities: Visible Browser, Code Execution, and Skill Bank.
    """
    def __init__(self, loop: asyncio.AbstractEventLoop = None):
        self.model = get_llm_model()
        self.loop = loop or asyncio.get_event_loop()
        
        target_path = settings.TARGET_WORKSPACE_PATH
        
        # 1. Search Tools (Serper only for high-fidelity)
        all_search_tools = SearchToolkit().get_tools()
        self.search_tools = []
        for t in all_search_tools:
            if hasattr(t, 'openai_tool_schema'):
                name = t.openai_tool_schema["function"]["name"]
                if "serper" in name.lower():
                    self.search_tools.append(t)
        
        # 2. Sentinel-Elite Toolkits
        self.browser_toolkit = BrowserToolkit(headless=False)
        self.code_exec_toolkit = CodeExecutionToolkit(sandbox="subprocess")
        self.skill_toolkit = SkillToolkit(working_directory="skills/")
        self.terminal_toolkit = TerminalToolkit(working_directory=target_path)
        self.file_toolkit = FileToolkit(working_directory=target_path)
        self.excel_toolkit = ExcelToolkit(working_directory=os.path.join(target_path, "report"))
        
        # 3. Combined Workforce Tools
        self.tools = wrap_toolkit_with_exclusion([
            *self.file_toolkit.get_tools(),
            *self.terminal_toolkit.get_tools(),
            *self.excel_toolkit.get_tools(),
            *self.browser_toolkit.get_tools(),
            *self.code_exec_toolkit.get_tools(),
            *self.skill_toolkit.get_tools(),
            *self.search_tools
        ])

        # 4. Build the underlying agent
        self.agent = ChatAgent(
            system_message=AUDITOR_SYS_MSG,
            model=self.model,
            tools=self.tools,
            token_limit=200000,
            summarize_threshold=80,
            prune_tool_calls_from_memory=True
        )
        
        logger.info(f"Auditor Agent upgraded to Sentinel-Elite for {target_path}")
