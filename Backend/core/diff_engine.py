import subprocess
import os
from core.settings import settings
import json
import logging

logger = logging.getLogger("hacker-society")

def get_target_path():
    # Strictly use the environment-provided path
    return settings.TARGET_WORKSPACE_PATH

def reset_victim_codebase():
    """
    Clears out previous patches in the target workspace safely.
    Uses checkout and clean instead of reset --hard to avoid wiping the entire repo.
    """
    path = get_target_path()
    if not path:
        logger.error("No TARGET_WORKSPACE_PATH set. Skipping reset.")
        return

    abs_path = os.path.abspath(path)
    logger.info(f"Safely resetting target workspace at: {abs_path}")
    
    if not os.path.exists(abs_path):
        logger.error(f"Target path does not exist: {abs_path}")
        return

    # Ensure the target directory is a git repository for diffing logic to work
    if not os.path.exists(os.path.join(abs_path, ".git")):
        logger.info(f"Target workspace not initialized as git. Running 'git init' in {abs_path}...")
        subprocess.run(["git", "init"], cwd=abs_path, capture_output=True, text=True)
        # Commit all initial files so we have a HEAD to diff against
        subprocess.run(["git", "add", "."], cwd=abs_path, capture_output=True, text=True)
        subprocess.run(["git", "commit", "-m", "Initial commit for security audit"], cwd=abs_path, capture_output=True, text=True)
        logger.info("Target workspace git setup complete.")

    try:
        # 1. Revert changes to tracked files in THIS directory only
        res1 = subprocess.run(["git", "checkout", "HEAD", "--", "."], cwd=abs_path, capture_output=True, text=True)
        if res1.returncode != 0:
            logger.error(f"Git checkout failed: {res1.stderr.strip()}")
        
        # 2. Remove untracked files in THIS directory only
        res2 = subprocess.run(["git", "clean", "-fd", "."], cwd=abs_path, capture_output=True, text=True)
        if res2.returncode == 0:
            logger.info("Target workspace reset successfully (non-destructive).")
        else:
            logger.error(f"Git clean failed: {res2.stderr.strip()}")
            
    except Exception as e:
        logger.error(f"Critical error during safety reset: {e}")

def capture_diff_payload():
    """
    Runs git diff on the target workspace and converts it to our JSON Stream array.
    """
    path = get_target_path()
    if not path:
        return []

    try:
        logger.info(f"Running git diff in {path}")
        # Run git diff relative to the target path
        result = subprocess.run(["git", "diff", "--name-only"], cwd=path, capture_output=True, text=True, check=True, errors="replace")
        changed_files = [f for f in result.stdout.strip().split('\n') if f]
        logger.info(f"Files changed: {changed_files}")
        
        diff_array = []
        for file in changed_files:
            file_abs_path = os.path.join(path, file)
            
            # Get old code from git HEAD
            old_code_proc = subprocess.run(["git", "show", f"HEAD:{file}"], cwd=path, capture_output=True, text=True, errors="replace")
            old_code = old_code_proc.stdout if old_code_proc.returncode == 0 else ""
            
            # Get new code from physical disk
            if os.path.exists(file_abs_path):
                with open(file_abs_path, "r", errors="replace") as f:
                    new_code = f.read()
            else:
                new_code = "[FILE DELETED]"
                
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
