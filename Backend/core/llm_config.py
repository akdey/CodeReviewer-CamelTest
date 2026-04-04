import os
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType

ACTIVE_PROVIDER = os.getenv("ACTIVE_PROVIDER", "groq")

def get_llm_model():
    if ACTIVE_PROVIDER.lower() == "openai":
        return ModelFactory.create(
            model_platform=ModelPlatformType.OPENAI,
            model_type=ModelType.GPT_4O_MINI,
        )
    elif ACTIVE_PROVIDER.lower() == "gemini":
        return ModelFactory.create(
            model_platform=ModelPlatformType.GEMINI,
            model_type=ModelType.GEMINI_1_5_PRO,
        )
    elif ACTIVE_PROVIDER.lower() == "azure":
        return ModelFactory.create(
            model_platform=ModelPlatformType.AZURE,
            model_type=ModelType.GPT_4O_MINI,
        )
    else:
        # Default to Groq since it's the fastest for terminal iteration
        return ModelFactory.create(
            model_platform=ModelPlatformType.GROQ,
            model_type=ModelType.GROQ_LLAMA_3_3_70B,
        )
