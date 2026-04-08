import os
from typing import List


def _parse_cors_origins(value: str) -> List[str]:
    """
    Parse comma-separated origins from env.
    Example:
    CORS_ORIGINS=https://my-app.azurestaticapps.net,http://localhost:5500
    """
    if not value:
        return ["*"]
    return [origin.strip() for origin in value.split(",") if origin.strip()]


# Database:
# - Local default: SQLite
# - Production (Azure): set DATABASE_URL to PostgreSQL URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./smart_task_manager.db")

# Auth
SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_THIS_SECRET_KEY_FOR_PRODUCTION")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

# CORS
CORS_ORIGINS = _parse_cors_origins(os.getenv("CORS_ORIGINS", "*"))

