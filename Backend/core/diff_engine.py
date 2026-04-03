import subprocess
import os
from core.settings import settings
import json
import logging

logger = logging.getLogger("hacker-society")

def get_target_path():
    return getattr(settings, "TARGET_WORKSPACE_PATH", os.path.join(os.getcwd(), "../targeted_source_code"))

def reset_victim_codebase():
    """
    Clears out all previous Fixer agent patches so the demonstration starts fresh!
    """
    path = os.path.abspath(get_target_path())
    logger.info(f"Attempting Git reset at absolute path: {path}")
    
    if not os.path.exists(path):
        logger.error(f"Target path does not exist: {path}")
        return

    try:
        # Capture stderr to see specifically why it is failing with 128
        res1 = subprocess.run(["git", "reset", "--hard"], cwd=path, capture_output=True, text=True)
        if res1.returncode != 0:
            logger.error(f"Git reset failed (status {res1.returncode}): {res1.stderr.strip()}")
        
        res2 = subprocess.run(["git", "clean", "-fd"], cwd=path, capture_output=True, text=True)
        if res2.returncode == 0:
            logger.info("Victim codebase reset successfully.")
        else:
            logger.error(f"Git clean failed: {res2.stderr.strip()}")
            
    except Exception as e:
        logger.error(f"Critical error during Git reset: {e}")

def capture_diff_payload():
    """
    Runs git diff on targeted_source_code and converts it to our JSON Stream array.
    """
    path = get_target_path()
    try:
        # We need the filenames that changed
        logger.info(f"Running git diff in {path}")
        result = subprocess.run(["git", "diff", "--name-only"], cwd=path, capture_output=True, text=True, check=True)
        changed_files = [f for f in result.stdout.strip().split('\n') if f]
        logger.info(f"Files changed: {changed_files}")
        
        diff_array = []
        for file in changed_files:
            # Get old code from git HEAD
            old_code_proc = subprocess.run(["git", "show", f"HEAD:{file}"], cwd=path, capture_output=True, text=True)
            old_code = old_code_proc.stdout
            
            # Get new code from physical disk
            with open(os.path.join(path, file), "r") as f:
                new_code = f.read()
                
            diff_array.append({
                "filename": file,
                "old_code": old_code,
                "new_code": new_code
            })
            
        logger.info(f"Captured diff for {len(diff_array)} files.")
        return diff_array
    except Exception as e:
        logger.error(f"Failed to capture diff: {e}")
        return []
