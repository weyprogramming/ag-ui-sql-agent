from typing import Literal

from pydantic import BaseModel, computed_field

from cryptography.fernet import Fernet

from settings import settings

SQLDependencyType = Literal["sqlite", "postgres", "mysql", "mssql"]


class SQLBaseDependencyCreateRequest(BaseModel):
    type: SQLDependencyType
    name: str
    host: str
    port: int
    database: str
    username: str
    password: str
    
    @computed_field
    @property
    def encrypted_password(self) -> str:
        return Fernet(settings.DB_PASSWORD_KEY).encrypt(self.password.encode()).decode()
    