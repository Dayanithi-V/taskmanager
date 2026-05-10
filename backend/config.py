import os
from typing import List, Set


def _parse_cors_origins(value: str) -> List[str]:
    """
    Parse comma-separated origins from env.
    Example:
    CORS_ORIGINS=https://my-app.azurestaticapps.net,http://localhost:5500
    """
    if not value:
        return ["*"]
    return [origin.strip() for origin in value.split(",") if origin.strip()]


def _parse_admin_emails(value: str) -> Set[str]:
    return {e.strip().lower() for e in (value or "").split(",") if e.strip()}


# Database:
# - Local default: SQLite
# - Production (Azure): set DATABASE_URL to PostgreSQL URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./smart_task_manager.db")

# Auth
SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_THIS_SECRET_KEY_FOR_PRODUCTION")
REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY", SECRET_KEY)
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Comma-separated emails that receive role "admin" on registration (lowercased match).
ADMIN_EMAILS_RAW = os.getenv("ADMIN_EMAILS", "")
ADMIN_EMAILS_SET = _parse_admin_emails(ADMIN_EMAILS_RAW)

# CORS
CORS_ORIGINS = _parse_cors_origins(os.getenv("CORS_ORIGINS", "*"))

# ML Prioritization
USE_ML_PRIORITIZATION = os.getenv("USE_ML_PRIORITIZATION", "false").lower() == "true"
ML_MODEL_PATH = os.getenv(
    "ML_MODEL_PATH", "backend/ml/model/priority_model.joblib"
)

# Azure Monitor / Application Insights (optional)
APPLICATIONINSIGHTS_CONNECTION_STRING = os.getenv(
    "APPLICATIONINSIGHTS_CONNECTION_STRING", ""
)

# Rate limiting (slowapi format, e.g. "100/minute")
RATE_LIMIT_DEFAULT = os.getenv("RATE_LIMIT_DEFAULT", "120/minute")
RATE_LIMIT_AUTH = os.getenv("RATE_LIMIT_AUTH", "20/minute")
