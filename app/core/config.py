"""
Application configuration settings using Pydantic.
"""

import os
from typing import List, Union

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings class."""

    PROJECT_NAME: str = "Report Generator"
    PROJECT_DESCRIPTION: str = "Meeting report generator from audio uploads"
    VERSION: str = "1.0.0"
    API_PREFIX: str = ""
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    DEV_MODE: bool = DEBUG

    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: List[str] = ["*"]

    @field_validator("CORS_ORIGINS")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse CORS origins from string to list if needed."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        # covers JSON-style list string, e.g. '["http://a.com", "http://b.com"]'
        elif isinstance(v, str):
            import json

            try:
                parsed = json.loads(v)
                if isinstance(parsed, list) and all(isinstance(i, str) for i in parsed):
                    return parsed
            except Exception:
                pass
        raise ValueError(
            f"CORS_ORIGINS must be a list of strings or a comma-separated string. cors value{v}"
        )

    # Database
    DB_ENGINE: str = os.getenv("DB_ENGINE", "sqlite")
    DB_USER: str = os.getenv("DB_USER", "")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_HOST: str = os.getenv("DB_HOST", "")
    DB_PORT: str = os.getenv("DB_PORT", "")
    DB_NAME: str = os.getenv("DB_NAME", "db.sqlite3")

    @property
    def DATABASE_URL(self) -> str:
        """Construct database URL based on configuration."""
        if self.DB_ENGINE == "sqlite":
            return f"sqlite+aiosqlite:///{self.DB_NAME}"
        elif self.DB_ENGINE == "postgresql":
            return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        return f"{self.DB_ENGINE}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def TEST_DATABASE_URL(self) -> str:
        """Construct database URL based on configuration."""
        if self.DB_ENGINE == "sqlite":
            return f"sqlite+aiosqlite:///{self.DB_NAME}-test"
        elif self.DB_ENGINE == "postgresql":
            return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}-test"
        return f"{self.DB_ENGINE}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}-test"

    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    MAX_UPLOAD_SIZE: int = int(
        os.getenv("MAX_UPLOAD_SIZE", "100000000")
    )  # 100MB default
    ALLOWED_AUDIO_EXTENSIONS: List[str] = [".mp3", ".wav", ".m4a"]

    ASSEMBLYAI_BASE_URL: str = os.getenv("ASSEMBLYAI_BASE_URL", "")
    ASSEMBLYAI_API_KEY: str = os.getenv("ASSEMBLYAI_API_KEY", "")

    MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY", "")
    MISTRAL_BASE_URL: str = os.getenv("MISTRAL_BASE_URL", "")
    DEFAULT_MISTRAL_MODEL: str = os.getenv(
        "DEFAULT_MISTRAL_MODEL", "mistral-medium-latest"
    )

    DEFAULT_REPORT_DIR: str = os.getenv("DEFAULT_REPORT_DIR", "reports")

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()
