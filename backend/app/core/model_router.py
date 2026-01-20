"""
Model router for selecting and initializing chat-capable LLMs.

IMPORTANT:
- This project does NOT use OpenAI-hosted models.
- We only use OpenAI-API-compatible providers:
  - OpenRouter (free models)
  - Local LLaMA server
"""

try:
    from langchain_openai import ChatOpenAI
    from langchain_core.language_models.chat_models import BaseChatModel
except Exception as e:
    print(f"[ModelRouter] Warning: LangChain import failed: {e}")
    ChatOpenAI = None
    BaseChatModel = object  # Dummy base class

from app.core.config import settings
from fastapi import HTTPException


OPENROUTER_MODELS = {
    "meta-llama/llama-3.3-70b-instruct:free",
    "mistralai/mistral-small-3.1-24b-instruct:free",
    "google/gemma-3-12b-it:free",
    "qwen/qwen3-next-80b-a3b-instruct:free",
    "nousresearch/hermes-3-llama-3.1-405b:free",
}

def get_llm(model_name: str) -> BaseChatModel:
    """
    Route model requests to the correct provider.
    """

    # 1️⃣ Local LLaMA (vLLM)
    if not ChatOpenAI:
        print("[ModelRouter] Error: ChatOpenAI not available")
        raise HTTPException(status_code=500, detail="AI Model service unavailable due to missing dependencies")

    if model_name.startswith("meta-llama/Llama-") and "local" in model_name:
        return ChatOpenAI(
            model=model_name,
            base_url=settings.local_llm_base_url,
            api_key=settings.local_llm_api_key or "dummy",
            temperature=0.2,
            timeout=30,
            max_retries=1,
            streaming=False,
        )

    # 2️⃣ OpenRouter models
    # If it's a known model or looks like a valid OpenRouter ID (vendor/model), use it.
    # Otherwise fallback.
    if model_name not in OPENROUTER_MODELS and "/" not in model_name:
         print(f"[ModelRouter] Warning: Invalid model '{model_name}'. Falling back.")
         model_name = "meta-llama/llama-3.3-70b-instruct:free"

    return ChatOpenAI(
        model=model_name,
        base_url=settings.openrouter_base_url,
        api_key=settings.openrouter_api_key,
        temperature=0.2,
        timeout=60, # Increased timeout
        max_retries=2,
    )
