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
        
        target_path = getattr(settings, "TARGET_WORKSPACE_PATH", os.path.join(os.getcwd(), "../targeted_source_code"))

        # Tools specifically for auditing: Search the web (Serper only)
        all_search_tools = SearchToolkit().get_tools()
        self.search_tools = []
        for t in all_search_tools:
            name = t.openai_tool_schema["function"]["name"]
            # Switch from duckduckgo to serper as requested
            if "serper" in name.lower():
                self.search_tools.append(t)
        
        # Apply the exclusion filter and output truncation to file tools
        self.file_tools = wrap_toolkit_with_exclusion(FileToolkit(working_directory=target_path).get_tools())

        self.agent = ChatAgent(
            system_message=AUDITOR_SYS_MSG,
            model=self.model,
            tools=[*self.search_tools, *self.file_tools]
        )
