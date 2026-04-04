import os
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

def get_llm_model():
    # Use function-level fetch to ensure most up-to-date values are used
    provider = os.getenv("ACTIVE_PROVIDER", "groq").lower()
    
    if provider == "openai":
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
        # Specific mapping for Azure OpenAI stability in CAMEL-AI SDK
        api_key = os.getenv("AZURE_OPENAI_API_KEY", "").strip('"')
        url = os.getenv("AZURE_OPENAI_ENDPOINT", "").strip('"')
        # Support both prefixed and direct environment variables
        api_version = (os.getenv("AZURE_API_VERSION") or os.getenv("AZURE_OPENAI_API_VERSION", "")).strip('"')
        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "").strip('"')

        return ModelFactory.create(
            model_platform=ModelPlatformType.AZURE,
            model_type=ModelType.GPT_4O_MINI,
            api_key=api_key,
            url=url,
            api_version=api_version,
            azure_deployment_name=deployment
        )
    else:
        # Default to Groq since it's the fastest for terminal iteration
        return ModelFactory.create(
            model_platform=ModelPlatformType.GROQ,
            model_type=ModelType.GROQ_LLAMA_3_3_70B,
        )
