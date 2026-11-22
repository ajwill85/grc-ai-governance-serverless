"""
Application Configuration
"""

from pydantic import model_validator
from pydantic_settings import BaseSettings
from typing import List
import os


# Local environments may start without SECRET_KEY and use the dev fallback.
_LOCAL_ENVIRONMENTS = {"local", "development", "dev", "test"}
_DEV_SECRET_KEY = "dev_secret_key_change_in_production"


class Settings(BaseSettings):
    # Project Info
    PROJECT_NAME: str = "AWS AI Governance Platform"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # API Settings
    API_V1_STR: str = "/api/v1"

    # Security
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://grc_user:grc_password_dev@localhost:5432/grc_governance"
    )

    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
    ]

    # AWS Settings
    AWS_REGION: str = "us-east-1"
    AWS_SCANNER_ROLE_NAME: str = "GRCGovernanceScanner"

    # Scanning
    MAX_CONCURRENT_SCANS: int = 5
    SCAN_TIMEOUT_MINUTES: int = 30

    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    @model_validator(mode="after")
    def require_secret_key_outside_local_dev(self):
        """Fail startup outside local development when SECRET_KEY is unset."""
        environment = (self.ENVIRONMENT or "").strip().lower()
        secret = (self.SECRET_KEY or "").strip()
        if secret:
            self.SECRET_KEY = secret
            return self
        if environment in _LOCAL_ENVIRONMENTS:
            self.SECRET_KEY = _DEV_SECRET_KEY
            return self
        raise ValueError(
            "SECRET_KEY must be set when ENVIRONMENT is not local "
            f"development (ENVIRONMENT={self.ENVIRONMENT!r})."
        )

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
