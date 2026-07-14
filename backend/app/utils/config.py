from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


# config.py -> utils -> app -> backend
BACKEND_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BACKEND_DIR / ".env"


class Settings(BaseSettings):
    app_name: str = "AI-First CRM HCP API"
    database_url: str = (
        "mysql+pymysql://root:Shubham@localhost:3306/ai_crm"
    )
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    frontend_origin: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()