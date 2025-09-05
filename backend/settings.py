from cryptography.fernet import Fernet

from pydantic_settings import BaseSettings, SettingsConfigDict

class SQLAgentSettings(BaseSettings):

    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None

    DB_PASSWORD_KEY: str = Fernet.generate_key().decode()
    
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='allow'
    )
    
settings = SQLAgentSettings()