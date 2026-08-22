import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./assawin.db"
    JWT_SECRET_KEY: str = "super_secret_assawin_key_2026"
    WORKER_INTERVAL_SECONDS: int = 600

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = Settings()
