import os
import logging
import os
import asyncio
from camel.societies.workforce import Workforce
from camel.tasks import Task
from core.llm_config import get_llm_model
from core.websocket_manager import ws_manager
from core.diff_engine import reset_victim_codebase, capture_diff_payload
from core.observed_agent import ObservedChatAgent
from core.workforce_tracking import SocketWorkforceCallback
from agents.auditor_agent import AuditorAgent
from agents.fixer_agent import FixerAgent
from agents.persona_setup import STRATEGIST_SYS_MSG
from features.recon_service import CodeReconService

logger = logging.getLogger("hacker-society")

class SecurityWorkforce:
    """
    Agentic security society responsible for the end-to-end mission lifecycle.
    Upgraded to Sentinel-Elite with visible browser, Code Execution, and Structural Recon.
    """
    def __init__(self, loop: asyncio.AbstractEventLoop):
        self.model = get_llm_model()
        self.loop = loop
        
        # Initialize basic directories
        os.makedirs("skills", exist_ok=True)
        from core.settings import settings
        os.makedirs(os.path.join(settings.TARGET_WORKSPACE_PATH, "report"), exist_ok=True)
        os.makedirs(os.path.join(settings.TARGET_WORKSPACE_PATH, ".sentinel_repro"), exist_ok=True)
        
        # 1. Instantiate the tool-equipped agents (Auditor & Fixer)
        self.auditor_wrapper = AuditorAgent(loop=self.loop)
        self.fixer_wrapper = FixerAgent(loop=self.loop)
        
        # 2. Instantiate the Recon Service (Documentation Architect)
        self.recon_service = CodeReconService(loop=self.loop)
        
        # 3. Enrich the OWL Strategist with Sentinel-Elite capabilities
        from core.utils import wrap_toolkit_with_exclusion
        from camel.toolkits import BrowserToolkit, SearchToolkit, CodeExecutionToolkit, SkillToolkit, TerminalToolkit
        
        # Initialize Toolkits
        self.strat_terminal = TerminalToolkit(working_directory=settings.TARGET_WORKSPACE_PATH)
        self.strat_browser = BrowserToolkit(headless=False)
        self.strat_code_exec = CodeExecutionToolkit(sandbox="subprocess")
        self.strat_skill = SkillToolkit(working_directory="skills/")
        self.strat_search = SearchToolkit()
        
        # Combine Strategist Tools
        all_strat_tools = [
            *self.strat_terminal.get_tools(),
            *self.strat_browser.get_tools(),
            *self.strat_code_exec.get_tools(),
            *self.strat_skill.get_tools(),
            self.strat_search.search_duckduckgo,
            self.strat_search.search_wiki
        ]
        
        self.strategist_tools = wrap_toolkit_with_exclusion(all_strat_tools)
        
        # 4. Define the Strategist
        self.strategist = ObservedChatAgent(
            system_message=STRATEGIST_SYS_MSG,
            model=self.model,
            tools=self.strategist_tools,
            agent_name="OWL Strategist",
            loop=self.loop,
            token_limit=200000,
            summarize_threshold=80,
            prune_tool_calls_from_memory=True
        )
        
        # 5. Create the CAMEL Workforce
        self.workforce = Workforce(
            "Autonomous Security Workforce",
            coordinator_agent=self.strategist,
            task_agent=self.strategist, 
            callbacks=[SocketWorkforceCallback(loop=self.loop)]
        )

        # 6. Attach Worker Nodes
        self.workforce.add_single_agent_worker(
            worker=self.auditor_wrapper.agent,
            description="Auditor: Scans for CVEs and secrets. Creates 'reproduction.py' PoCs using CodeExecutionToolkit."
        )

        self.workforce.add_single_agent_worker(
            worker=self.fixer_wrapper.agent,
            description="Fixer: Applies patches and verifies them against the Auditor's reproduction PoCs."
        )

    def broadcast_sync(self, stream_type: str, data: dict):
        if self.loop:
            asyncio.run_coroutine_threadsafe(ws_manager.broadcast_json(stream_type, data), self.loop)

    def run_mission(self):
        logger.info("Executing Sentinel-Elite Mission Setup (with Intel Phase)...")
        reset_victim_codebase()
        
        self.broadcast_sync("system", {"message": "Mission Started: Initiating Structural Reconnaissance..."})
        
        # PHASE 1: Code Recon (Generate Documentation)
        # We use run_coroutine_threadsafe because this method is called from BackgroundTasks
        recon_future = asyncio.run_coroutine_threadsafe(self.recon_service.run_recon(), self.loop)
        recon_future.result() # Wait for recon to finish
        
        # PHASE 2: Context Injection
        intel_briefing = self.recon_service.get_context_for_audit()
        
        self.broadcast_sync("system", {"message": "Intelligence Briefing Ready. Commencing Security Mission..."})
        
        global_task = (
            "Execute a Sentinel-Elite security mission with the following INTELLIGENCE BRIEFING:\n"
            f"{intel_briefing}\n\n"
            "MISSION OBJECTIVES:\n"
            "1. **Secret Hunting**: Hunt for API keys and credentials across the codebase via 'grep'/'rg'. Report finding in 'report/vulnerability-audit.md'.\n"
            "2. **Excel CVE Dashboard**: Research library vulns (via SearchToolkit) and generate 'report/vulnerability_dashboard.xlsx' using ExcelToolkit.\n"
            "3. **Safe Patch & Verification**: Apply patches using ONLY FileToolkit (NO 'sed'). Run '.sentinel_repro/reproduction.py' pre and post fix.\n"
            "4. **Automated Testing**: Run 'pytest' or 'uv run pytest' after fixes and save output to 'report/test-results.md'.\n"
            "5. **Centralized Reporting**: ALL mission summaries and logic logs MUST be in the 'report/' directory."
        )

        task = Task(content=global_task)
        result_task = self.workforce.process_task(task)
        result = result_task.result
        
        # Capture Diffs and wrap up
        diff_payload = capture_diff_payload()
        if diff_payload: self.broadcast_sync("diff_stream", {"files": diff_payload})
        self.broadcast_sync("system", {"message": "Sentinel-Elite Mission Complete."})
