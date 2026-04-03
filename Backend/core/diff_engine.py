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
        # We need the filenames that changed within the target folder
        logger.info(f"Running git diff in {path}")
        # Run git diff from the root, filtering by the targeted source code folder
        result = subprocess.run(["git", "diff", "--name-only", "--", path], capture_output=True, text=True, check=True)
        changed_files = [f for f in result.stdout.strip().split('\n') if f]
        logger.info(f"Files changed: {changed_files}")
        
        diff_array = []
        for file in changed_files:
            # Get old code from git HEAD (file returns relative to root repo, e.g. targeted_source_code/app.py)
            old_code_proc = subprocess.run(["git", "show", f"HEAD:{file}"], capture_output=True, text=True)
            old_code = old_code_proc.stdout
            
            # Get new code from physical disk
            # file is already a valid relative path from the root project folder where the server is running
            with open(file, "r") as f:
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
