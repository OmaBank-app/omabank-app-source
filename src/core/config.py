import os
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application State
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "dev")
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "OmaBank Core Ledger API"

    # Infrastructure Hooks (Injected via Azure DevOps/Kubernetes ConfigMaps)
    KEY_VAULT_URL: Optional[str] = os.getenv("KEY_VAULT_URL")

    # Internal Network Endpoints
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # These will be dynamically loaded from the Azure Key Vault at runtime
    DATABASE_URL: Optional[str] = None
    JWT_SECRET_KEY: Optional[str] = None

    class Config:
        case_sensitive = True


settings = Settings()
