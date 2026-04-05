from fastapi import APIRouter, BackgroundTasks
from agents.society import SecurityWorkforce
from core.websocket_manager import ws_manager
from core.settings import settings
import asyncio
import logging

logger = logging.getLogger("hacker-society")

router = APIRouter()

@router.post("/start_audit")
async def start_audit(background_tasks: BackgroundTasks):
    """
    Triggers the autonomous SecurityWorkforce loop.
    Pushed to BackgroundTasks so the HTTP request resolves immediately for the frontend.
    """
    # Capture the main thread's running loop BEFORE sending to the background threadpool
    main_loop = asyncio.get_running_loop()
    
    # Run the mission and its initialization in a separate threadpool 
    def run_mission_sync(loop_to_use):
        try:
            society = SecurityWorkforce(loop=loop_to_use)
            logger.info("Starting background Security Workforce mission...")
            society.run_mission()
            logger.info("Background mission finished successfully.")
        except Exception as e:
            logger.error(f"Mission failed in background: {e}", exc_info=True)
        
    background_tasks.add_task(run_mission_sync, main_loop)
    
    return {"status": "success", "message": "Security Workforce objective deployed onto non-deterministic loop!"}
