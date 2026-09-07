from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

env_path = Path(__file__).resolve().parent.parent.parent.parent / ".env"

class Settings(BaseSettings):
    database_url: str
    api_host: str
    api_port: int
    cors_origins: str

    model_config = SettingsConfigDict(env_file=str(env_path), extra="ignore")

settings = Settings()