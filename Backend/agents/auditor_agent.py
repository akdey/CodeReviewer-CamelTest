import os
from camel.agents import ChatAgent
from camel.toolkits import FileToolkit, SearchToolkit
from core.settings import settings
from core.llm_config import get_llm_model
from agents.persona_setup import AUDITOR_SYS_MSG

class AuditorAgent:
    def __init__(self):
        self.model = get_llm_model()
        
        target_path = os.path.join(os.getcwd(), "../targeted_source_code")

        # Tools specifically for auditing: Read local files, and search the web (DDG only)
        # We filter out SerpAPI/Serper to avoid "api_key_required" errors.
        all_search_tools = SearchToolkit().get_tools()
        self.search_tools = []
        for t in all_search_tools:
            # FunctionTool objects in CAMEL store the name in the OpenAI schema
            name = t.openai_tool_schema["function"]["name"]
            if "duckduckgo" in name.lower():
                self.search_tools.append(t)
        
        self.file_tools = FileToolkit(working_directory=target_path).get_tools()

        self.agent = ChatAgent(
            system_message=AUDITOR_SYS_MSG,
            model=self.model,
            tools=[*self.search_tools, *self.file_tools]
        )
