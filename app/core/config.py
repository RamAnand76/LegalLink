from typing import List, Optional, Union
from pydantic import AnyHttpUrl, EmailStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    API_STR: str = "/api"
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    PROJECT_NAME: str

    SQLALCHEMY_DATABASE_URL: str

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env")


settings = Settings()
