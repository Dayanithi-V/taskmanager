from typing import Any, Dict

from fastapi import APIRouter
from sqlalchemy import text

from ..database import engine

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> Dict[str, Any]:
    """
    Liveness + dependency probe for load balancers and monitors.
    """
    db_status = "unknown"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "error"

    overall = "healthy" if db_status == "connected" else "degraded"
    return {"status": overall, "database": db_status}
