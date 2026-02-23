from typing import List, Optional, Union
from pydantic import AnyHttpUrl, EmailStr, field_validator, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_STR: str = "/api"
    SECRET_KEY: str = "super-secret-key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    PROJECT_NAME: str = "LegalLink"

    SQLALCHEMY_DATABASE_URL: str = "sqlite:///./test.db"


    # OpenRouter Configuration
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = "google/gemini-2.0-flash-exp:free"
    OPENROUTER_SITE_URL: str = "http://localhost:8000"
    OPENROUTER_SITE_NAME: str = "LegalLink"

    # Free models to rotate through on rate limit
    OPENROUTER_FALLBACK_MODELS: List[str] = [
        "google/gemini-2.0-flash-exp:free",
        "meta-llama/llama-3.2-3b-instruct:free",
        "microsoft/phi-3-mini-128k-instruct:free",
        "mistralai/mistral-7b-instruct:free",
        "openchat/openchat-7b:free",
        "gryphe/mythomax-l2-13b:free",
        "nousresearch/hermes-3-llama-3.1-405b:free",
    ]
    
    # Toggle for auto-switching models
    ENABLE_MODEL_FALLBACK: bool = True

    # Provider switch
    PROVIDER: str = "openrouter"  # possible values: "openrouter", "openai", "gemini"

    # OpenAI Configuration (optional)
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-3.5-turbo"

    # Gemini Configuration
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # RAG Configuration
    DOCS_PATH: str = "docs"  # Path to documents for RAG
    FAISS_INDEX_PATH: str = "faiss_index"  # Path to store FAISS index

    model_config = ConfigDict(case_sensitive=True, env_file=".env")


settings = Settings()
