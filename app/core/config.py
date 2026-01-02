from typing import List, Optional, Union
from pydantic import AnyHttpUrl, EmailStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    API_STR: str = "/api"
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    PROJECT_NAME: str

    SQLALCHEMY_DATABASE_URL: str

    # OpenRouter Configuration
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = "google/gemini-2.0-flash-exp:free"
    OPENROUTER_SITE_URL: str = "http://localhost:8000"
    OPENROUTER_SITE_NAME: str = "LegalLink"

    # RAG Configuration
    DOCS_PATH: str = "docs"  # Path to documents for RAG
    FAISS_INDEX_PATH: str = "faiss_index"  # Path to store FAISS index

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env")


settings = Settings()
