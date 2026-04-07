import os
import shutil
import asyncio
import logging
import aiofiles
from fastapi import APIRouter, BackgroundTasks, UploadFile, File, Form, HTTPException
from typing import Optional
from core.settings import settings
from core.utils import extract_zip, clone_git_repo
from agents.society import SecurityWorkforce

logger = logging.getLogger("hacker-society")

router = APIRouter()

@router.post("/provision")
async def provision_workspace(
    file: Optional[UploadFile] = File(None),
    repo_url: Optional[str] = Form(None)
):
    """
    Consolidated provisioning endpoint. Handles ZIP uploads and Git cloning.
    ZIP takes precedence if both are provided.
    """
    target_path = settings.TARGET_WORKSPACE_PATH
    if not target_path:
        raise HTTPException(status_code=500, detail="TARGET_WORKSPACE_PATH not configured in .env")

    abs_target_path = os.path.abspath(target_path)
    os.makedirs(os.path.dirname(abs_target_path), exist_ok=True)
    
    metadata = {}
    if file and repo_url:
        metadata["warning"] = "Both ZIP and Git URL provided. Prioritizing ZIP file ingestion."
        logger.warning(f"Provisioning conflict: {metadata['warning']}")

    try:
        if file:
            # Handle ZIP Upload
            temp_zip_path = f"/tmp/uploaded_{file.filename}"
            logger.info(f"Ingesting ZIP: {file.filename} -> {temp_zip_path}")
            async with aiofiles.open(temp_zip_path, "wb") as out_file:
                content = await file.read()
                await out_file.write(content)
            
            # Safe extraction logic from core.utils
            extract_zip(temp_zip_path, abs_target_path)
            os.remove(temp_zip_path)
            metadata["source"] = f"ZIP_{file.filename}"
        
        elif repo_url:
            # Handle Git Clone logic from core.utils
            clone_git_repo(repo_url, abs_target_path)
            metadata["source"] = f"GIT_{repo_url}"
        
        else:
            raise HTTPException(status_code=400, detail="No source (ZIP or Git URL) provided for provisioning.")

        logger.info(f"Provisioning successful: {metadata['source']} localized at {abs_target_path}")
        return {"status": "success", "message": f"Workspace provisioned from {metadata['source']}", "metadata": metadata}

    except Exception as e:
        logger.error(f"Provisioning failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Provisioning sequence failed: {str(e)}")

@router.post("/start_audit")
async def start_audit(background_tasks: BackgroundTasks):
    """
    Triggers the autonomous SecurityWorkforce mission loop.
    Deploys onto a background thread to ensure real-time terminal and neural stream agility.
    """
    main_loop = asyncio.get_running_loop()
    
    def run_mission_sync(loop_to_use):
        try:
            logger.info("Initializing background Security Workforce...")
            society = SecurityWorkforce(loop=loop_to_use)
            logger.info("Deploying Agentic Mission objective...")
            society.run_mission()
            logger.info("Mission objective complete.")
        except Exception as e:
            logger.error(f"Mission failed in background: {e}", exc_info=True)
        
    background_tasks.add_task(run_mission_sync, main_loop)
    
    return {"status": "success", "message": "Autonomous mission objective deployed into the kinetic loop!"}
