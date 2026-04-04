from camel.societies.workforce import Workforce
from camel.tasks import Task
from core.llm_config import get_llm_model
from core.websocket_manager import ws_manager
from core.diff_engine import reset_victim_codebase, capture_diff_payload
import logging
import asyncio

logger = logging.getLogger("hacker-society")

from agents.auditor_agent import AuditorAgent
from agents.fixer_agent import FixerAgent
from camel.agents import ChatAgent
from agents.persona_setup import STRATEGIST_SYS_MSG
from core.tracking import track_agent
from core.workforce_tracking import SocketWorkforceCallback

class HackerSociety:
    def __init__(self, loop: asyncio.AbstractEventLoop):
        self.model = get_llm_model()
        self.loop = loop
        
        # 1. Instantiate the explicit tool-equipped workers
        self.auditor = track_agent(AuditorAgent().agent, "Security Auditor", self.loop)
        self.fixer = track_agent(FixerAgent().agent, "SETA Fixer", self.loop)
        
        # 2. Define the Strategist directly.
        self.strategist = track_agent(
            ChatAgent(
                system_message=STRATEGIST_SYS_MSG,
                model=self.model,
                tools=[]
            ),
            "OWL Strategist",
            self.loop
        )
        
        # 3. Create the CAMEL Workforce with explicit coordinator/task agents
        # and our custom real-time socket tracking callback.
        self.workforce = Workforce(
            "Hacker Society Workforce",
            coordinator_agent=self.strategist,
            task_agent=self.strategist, # Using strategist for both decomposition and task routing
            callbacks=[SocketWorkforceCallback(loop=self.loop)]
        )

        # 4. Attach Worker Nodes with Explicit Descriptions for the Task Router
        self.workforce.add_single_agent_worker(
            worker=self.auditor,
            description="Auditor: Searches for CVE vulnerabilities and reads requirements/pyproject.toml files physically via FileToolkit."
        )

        self.workforce.add_single_agent_worker(
            worker=self.fixer,
            description="Fixer: Executes shell commands to patch code via TerminalToolkit, and writes Python files natively via FileToolkit."
        )

    def broadcast_sync(self, stream_type: str, data: dict):
        """
        Dispatches a broadcast to the main thread's event loop safely.
        """
        asyncio.run_coroutine_threadsafe(
            ws_manager.broadcast_json(stream_type, data),
            self.loop
        )

    def run_mission(self):
        """
        Executes the CAMEL Workforce natively!
        """
        # Step 0: Ensure the victim codebase is entirely reset before we start.
        logger.info("Resetting victim codebase...")
        reset_victim_codebase()
        
        self.broadcast_sync("communications_stream", {
            "speaker": "System", 
            "text": "Target workspace Staged/Reset. Workforce initialized. Awaiting task execution."
        })
        
        self.broadcast_sync("system", {"message": "Mission Started: Vulnerability Research & Patching"})
        logger.info("Mission started.")

        global_task = (
            "Scan the entire target workspace to find vulnerabilities, open secrets, "
            "and poor code practices. Patch them appropriately and verify all fixes "
            "via pytest within the same environment."
        )

        # Fire off the CAMEL Workforce Loop natively
        task = Task(content=global_task)
        result_task = self.workforce.process_task(task)
        result = result_task.result
        logger.info(f"Workforce mission final result: {result}")

        self.broadcast_sync("communications_stream", {
            "speaker": "Hacker Society", 
            "text": f"MISSION COMPLETE. SUMMARY:\n{result}"
        })
        
        # Step End: Capture the Git Diff and beam it to the frontend!
        diff_payload = capture_diff_payload()
        if diff_payload:
            self.broadcast_sync("diff_stream", {
                "files": diff_payload
            })
            
        self.broadcast_sync("communications_stream", {
            "speaker": "System", 
            "text": f"Workforce task terminal objective complete.\nCode Differentiator Published."
        })
        
        self.broadcast_sync("system", {"message": "Mission Objective Completed. System Secured."})
        logger.info("Mission objective completed.")

