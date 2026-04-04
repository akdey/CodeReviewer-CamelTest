import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Strictly use the environment variable. If not provided, it will be None.
    # The agents and diff engine must handle this to ensure no accidental folder appending.
    TARGET_WORKSPACE_PATH = os.getenv("TARGET_WORKSPACE_PATH")

settings = Settings()
