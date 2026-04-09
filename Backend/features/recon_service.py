import os
import logging
import asyncio
from typing import List, Dict
from agents.architect_agent import StructuralArchitectAgent
from camel.datagen.source2synth.data_processor import UserDataProcessor
from camel.datagen.source2synth.user_data_processor_config import ProcessorConfig
from features.indexed_retriever import IndexedRetriever
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
        self.retriever = IndexedRetriever()
        
        # Initialize Source2Synth processor
        config = ProcessorConfig()
        self.processor = UserDataProcessor(config=config)

    async def run_recon(self):
        """
        Runs the documentation mission: Scan -> Map -> Synthesize.
        """
        target_path = settings.TARGET_WORKSPACE_PATH
        doc_path = os.path.join(target_path, "report")
        os.makedirs(doc_path, exist_ok=True)
        
        await ws_manager.broadcast_json("system", {
            "message": "Sentinel-Elite Recon: Mapping codebase hierarchy...",
            "type": "intelligence_update"
        })
        
        # 1. Structural Mapping & Hotspot Detection
        hotspots = self._map_hotspots(target_path)
        
        # 2. Semantic Indexing (RAG)
        await ws_manager.broadcast_json("system", {
            "message": "Sentinel-Elite Recon: Building semantic index (Vector RAG)...",
            "type": "intelligence_update"
        })
        self.retriever.index_codebase(target_path)
        
        # 3. Structural & Architectural Analysis
        hotspot_str = "\n".join([f"- {h}" for h in hotspots[:10]])
        arch_prompt = (
            f"Analyze the codebase at {target_path}.\n"
            f"IDENTIFIED HOTSPOTS:\n{hotspot_str}\n\n"
            "MISSION:\n"
            "1. Generate 'report/architecture.md'. Include a Mermaid.js diagram showing the core system components.\n"
            "2. Generate 'report/api-spec.md'. Scan for all API endpoints, request/response models, and authentication requirements.\n"
            "3. Generate 'report/data-flow.md'. Use 'semantic_code_search' to trace how data moves from user input to storage/output."
        )
        
        self.architect.agent.step(arch_prompt)
        
        # 4. Deep Security Mapping (Synthesize)
        security_prompt = (
            "Scan the identified hotspots and create a 'Security Perimeter' document in 'report/security-layout.md'.\n"
            "Highlight where validation, auth, and sensitive IO occur.\n"
            "Ensure all file paths are absolute and clickable."
        )
        self.architect.agent.step(security_prompt)
        
        await ws_manager.broadcast_json("system", {
            "message": "Scientific Intelligence Harvested: Comprehensive document tree available in 'report/'.",
            "type": "intelligence_complete"
        })
        
    def _map_hotspots(self, root_path: str) -> List[str]:
        """
        Recursively scans the directory structure to identify security hotspots.
        """
        hotspots = []
        security_keywords = {"auth", "crypto", "secret", "key", "token", "password", "identity", "admin", "db"}
        
        for root, dirs, files in os.walk(root_path):
            # Ignore hidden dirs and usual suspects
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in {'node_modules', '__pycache__', 'venv', '.venv'}]
            
            for name in files + dirs:
                if any(kw in name.lower() for kw in security_keywords):
                    rel_path = os.path.relpath(os.path.join(root, name), root_path)
                    hotspots.append(rel_path)
                    
        return sorted(list(set(hotspots)))

    @staticmethod
    def get_context_for_audit() -> str:
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
