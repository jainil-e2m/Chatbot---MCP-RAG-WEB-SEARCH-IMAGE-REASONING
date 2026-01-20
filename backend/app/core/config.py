"""
Configuration management for the AI Chatbot Platform.

NOTE:
This project does NOT use OpenAI-hosted models.
We only use OpenAI-compatible APIs (OpenRouter, Local LLaMA).
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Application
    app_name: str = "AI Chatbot Platform"
    debug: bool = True

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # OpenRouter (Hosted models)
    openrouter_api_key: Optional[str] = None
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    # Local LLaMA (OpenAI-compatible server)
    local_llm_base_url: Optional[str] = None
    local_llm_api_key: Optional[str] = None

    # Supabase Database
    supabase_url: str
    supabase_key: str

    # JWT Authentication
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60 * 24 * 7  # 7 days

    # Tavily Web Search
    tavily_api_key: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


settings = Settings()


