import os
from camel.agents import ChatAgent
from camel.toolkits import FileToolkit, SearchToolkit
from core.settings import settings
from core.llm_config import get_llm_model
from core.utils import wrap_toolkit_with_exclusion
from agents.persona_setup import AUDITOR_SYS_MSG

class AuditorAgent:
    def __init__(self):
        self.model = get_llm_model()
        
        # Strictly use target workspace from environment settings
        target_path = settings.TARGET_WORKSPACE_PATH
        if not target_path:
            raise ValueError("TARGET_WORKSPACE_PATH must be set in the environment/.env file.")

        # Search Tools (Serper only)
        all_search_tools = SearchToolkit().get_tools()
        self.search_tools = []
        for t in all_search_tools:
            name = t.openai_tool_schema["function"]["name"]
            if "serper" in name.lower():
                self.search_tools.append(t)
        
        # Initialize FileToolkit with the exact environment path
        raw_file_tools = FileToolkit(working_directory=target_path).get_tools()
        # Apply the exclusion filter and output truncation to file tools
        self.file_tools = wrap_toolkit_with_exclusion(raw_file_tools)

        self.agent = ChatAgent(
            system_message=AUDITOR_SYS_MSG,
            model=self.model,
            tools=[*self.search_tools, *self.file_tools]
        )
