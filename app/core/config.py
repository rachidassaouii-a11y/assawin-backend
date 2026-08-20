import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./assawin.db")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "super_secret_assawin_key_2026")
    WORKER_INTERVAL_SECONDS: int = int(os.getenv("WORKER_INTERVAL_SECONDS", "600"))

settings = Settings()
