import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    TARGET_WORKSPACE_PATH = os.getenv("TARGET_WORKSPACE_PATH", os.path.join(os.getcwd(), "../targeted_source_code"))

settings = Settings()
