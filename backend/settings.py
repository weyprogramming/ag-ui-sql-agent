from cryptography.fernet import Fernet

from pydantic_settings import BaseSettings, SettingsConfigDict

class DashboardAgentSettings(BaseSettings):

    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None
    
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    DB_PASSWORD_KEY: str
    
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='allow'
    )
    
settings = DashboardAgentSettings()