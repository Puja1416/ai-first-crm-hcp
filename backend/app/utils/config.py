from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI-First CRM HCP API"
    database_url: str = "mysql+pymysql://root:password@localhost:3306/ai_crm"
    groq_api_key: str = ""
    groq_model: str = "gemma2-9b-it"
    frontend_origin: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
