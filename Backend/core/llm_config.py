import os
import logging
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType
from dotenv import load_dotenv

logger = logging.getLogger("hacker-society")

# Ensure environment variables are loaded
load_dotenv()

def get_llm_model():
    """
    Returns the configured LLM model backend based on ACTIVE_PROVIDER.
    Ensures that placeholder keys like 'sk-...' are NOT used.
    """
    provider = os.getenv("ACTIVE_PROVIDER", "groq").lower()
    
    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key or api_key.startswith("sk-..."):
            logger.error("Invalid OPENAI_API_KEY detected. Please update .env.")
        return ModelFactory.create(
            model_platform=ModelPlatformType.OPENAI,
            model_type=ModelType.GPT_4O_MINI,
        )
    elif provider == "gemini":
        return ModelFactory.create(
            model_platform=ModelPlatformType.GEMINI,
            model_type=ModelType.GEMINI_1_5_PRO,
        )
    elif provider == "azure":
        api_key = os.getenv("AZURE_OPENAI_API_KEY", "").strip('"')
        url = os.getenv("AZURE_OPENAI_ENDPOINT", "").strip('"')
        api_version = (os.getenv("AZURE_API_VERSION") or os.getenv("AZURE_OPENAI_API_VERSION", "")).strip('"')
        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "").strip('"')

        if not api_key or "sk-" in api_key: # Safety check
            logger.error("Azure API Key appears invalid or placeholder.")

        return ModelFactory.create(
            model_platform=ModelPlatformType.AZURE,
            model_type=ModelType.GPT_4O_MINI,
            api_key=api_key,
            url=url,
            api_version=api_version,
            azure_deployment_name=deployment
        )
    else:
        # Default to Groq
        return ModelFactory.create(
            model_platform=ModelPlatformType.GROQ,
            model_type=ModelType.GROQ_LLAMA_3_3_70B,
        )
