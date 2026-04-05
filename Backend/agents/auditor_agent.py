import os
from camel.agents import ChatAgent
from camel.toolkits import FileToolkit, SearchToolkit, TerminalToolkit
from core.settings import settings
from core.llm_config import get_llm_model
from core.utils import wrap_toolkit_with_exclusion
from agents.persona_setup import AUDITOR_SYS_MSG

class AuditorAgent:
    def __init__(self):
        self.model = get_llm_model()
        
        # Strictly use target workspace from environment settings
        target_path = settings.TARGET_WORKSPACE_PATH
        # Search Tools (Serper only)
        all_search_tools = SearchToolkit().get_tools()
        self.search_tools = []
        for t in all_search_tools:
            name = t.openai_tool_schema["function"]["name"]
            if "serper" in name.lower():
                self.search_tools.append(t)
        
        # Initialize Toolkits with the exact environment path
        self.terminal_toolkit = TerminalToolkit(working_directory=target_path)
        self.file_toolkit = FileToolkit(working_directory=target_path)
        
        # Combine and wrap tools with exclusion/truncation logic
        self.file_tools = wrap_toolkit_with_exclusion(self.file_toolkit.get_tools())
        self.terminal_tools = wrap_toolkit_with_exclusion(self.terminal_toolkit.get_tools())

        self.agent = ChatAgent(
            system_message=AUDITOR_SYS_MSG,
            model=self.model,
            tools=[*self.search_tools, *self.file_tools, *self.terminal_tools]
        )
