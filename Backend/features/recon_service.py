import os
import logging
import asyncio
from typing import List, Dict
from agents.architect_agent import StructuralArchitectAgent
from camel.datagen.source2synth.data_processor import UserDataProcessor
from camel.datagen.source2synth.user_data_processor_config import ProcessorConfig
from core.settings import settings
from core.websocket_manager import ws_manager

logger = logging.getLogger("hacker-society")

class CodeReconService:
    """
    Orchestrates the codebase documentation phase using CAMEL agents and Source2Synth.
    """
    def __init__(self, loop: asyncio.AbstractEventLoop):
        self.loop = loop
        self.architect = StructuralArchitectAgent(loop=self.loop)
        
        # Initialize Source2Synth processor
        config = ProcessorConfig()
        self.processor = UserDataProcessor(config=config)

    async def run_recon(self):
        """
        Runs the documentation mission: Scan -> Synthesize -> Persist.
        """
        target_path = settings.TARGET_WORKSPACE_PATH
        doc_path = os.path.join(target_path, "report")
        os.makedirs(doc_path, exist_ok=True)
        
        await ws_manager.broadcast_json("system", {"message": "Structural Architect: Commencing Codebase Reconnaissance..."})
        
        # 1. Structural Scan Instruction
        prompt = (
            f"Analyze the codebase at {target_path}.\n"
            "1. List all main directories and their obvious purpose.\n"
            "2. Identify the entry point of the application.\n"
            "3. Create a high-level summary of the architectural flow.\n"
            f"Write your findings as 'architecture.md' in the 'report/' folder."
        )
        
        # Execute via the architect agent
        # We manually step the agent to ensure deep analysis
        response = self.architect.agent.step(prompt)
        
        # 2. Functional Synthesis (Deep Dive)
        # We'll have the agent list files, then we pick a few interesting ones to synth
        # (Simplified for now: requesting a module mapping)
        module_prompt = (
            "Create a module-wise analysis of the system.\n"
            "Focus on how data moves through the application.\n"
            f"Write this to 'module-analysis.md' in the 'report/' folder."
        )
        self.architect.agent.step(module_prompt)
        
        await ws_manager.broadcast_json("system", {"message": "Intelligence Synthesized: documentation stored in 'report/' folder."})
        
    def get_context_for_audit(v) -> str:
        """
        Reads the generated docs to provide context to other agents.
        """
        target_path = settings.TARGET_WORKSPACE_PATH
        doc_files = ["architecture.md", "module-analysis.md"]
        context_blocks = []
        
        for f in doc_files:
            p = os.path.join(target_path, "report", f)
            if os.path.exists(p):
                with open(p, 'r') as file:
                    context_blocks.append(f"### {f}\n{file.read()}")
        
        return "\n\n".join(context_blocks)
