import os
import logging
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

logger = logging.getLogger("hacker-society")

class SecurityWorkforce:
    """
    Agentic security society responsible for the end-to-end mission lifecycle.
    Restored with high-fidelity telemetry and verified tool schema fixes.
    """
    def __init__(self, loop: asyncio.AbstractEventLoop):
        self.model = get_llm_model()
        self.loop = loop
        
        # 1. Instantiate the tool-equipped agents (Auditor & Fixer)
        # These now use wrap_toolkit_with_exclusion internally
        self.auditor_wrapper = AuditorAgent(loop=self.loop)
        self.fixer_wrapper = FixerAgent(loop=self.loop)
        
        # 2. Define the Strategist directly as an ObservedChatAgent
        self.strategist = ObservedChatAgent(
            system_message=STRATEGIST_SYS_MSG,
            model=self.model,
            tools=[],
            agent_name="OWL Strategist",
            loop=self.loop
        )
        
        # 3. Create the CAMEL Workforce with custom socket tracking
        self.workforce = Workforce(
            "Autonomous Security Workforce",
            coordinator_agent=self.strategist,
            task_agent=self.strategist, 
            callbacks=[SocketWorkforceCallback(loop=self.loop)]
        )

        # 4. Attach Worker Nodes with Explicit Mission Roles
        self.workforce.add_single_agent_worker(
            worker=self.auditor_wrapper.agent,
            description="Auditor: Scans for CVEs and hardcoded secrets using FileToolkit and search. MUST confirm by reading files physically."
        )

        self.workforce.add_single_agent_worker(
            worker=self.fixer_wrapper.agent,
            description="Fixer: Executes terminal logic (uv, pytest) and applies code patches via FileToolkit."
        )

    def broadcast_sync(self, stream_type: str, data: dict):
        """Thread-safe mission telemetry dispatch."""
        if self.loop:
            asyncio.run_coroutine_threadsafe(
                ws_manager.broadcast_json(stream_type, data),
                self.loop
            )

    def run_mission(self):
        """Executes the complete Mission Objective Lifecycle."""
        logger.info("Executing Mission Setup...")
        reset_victim_codebase()
        
        # Initialize Report Directory in workspace
        from core.settings import settings
        report_path = os.path.join(settings.TARGET_WORKSPACE_PATH, "report")
        os.makedirs(report_path, exist_ok=True)
        
        self.broadcast_sync("communications_stream", {
            "speaker": "System", 
            "text": "Target workspace Reset. Reporting channel 'report/' opened. Workforce deployed."
        })
        
        self.broadcast_sync("system", {"message": "Mission Started: Vulnerability Research & Patching"})
        logger.info("Mission started.")

        global_task = (
            "Perform a comprehensive security audit and patching mission on the target workspace.\n\n"
            "1. **Audit**: Scan for vulnerable package versions and confirmed secrets. You MUST read files physically to confirm findings.\n"
            "2. **Patch**: Apply physical code edits to fix ALL identified issues. Logging them is insufficient.\n"
            "3. **Verify**: Use 'uv venv' and 'uv run pytest' to verify fixes.\n"
            "4. **Reporting**: You MUST generate all final mission outcomes as .md files inside the 'report/' folder in the workspace root."
        )

        # Process mission through CAMEL society
        task = Task(content=global_task)
        result_task = self.workforce.process_task(task)
        result = result_task.result
        logger.info(f"Workforce mission final results: {result}")

        self.broadcast_sync("communications_stream", {
            "speaker": "Security Workforce", 
            "text": f"MISSION COMPLETE. SUMMARY:\n{result}\n\nAll reports localized in 'report/' directory."
        })
        
        # Capture Final Work Diffs
        diff_payload = capture_diff_payload()
        if diff_payload:
            self.broadcast_sync("diff_stream", {"files": diff_payload})
            
        self.broadcast_sync("communications_stream", {
            "speaker": "System", 
            "text": "Workforce mission objective complete. Code Differentiator Published."
        })
        
        self.broadcast_sync("system", {"message": "Mission Objective Completed. System Secured."})
        logger.info("Mission objective completed.")
