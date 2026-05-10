from fastapi import APIRouter, Depends

from ..auth_utils import require_roles

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/ping")
def admin_ping(_admin=Depends(require_roles("admin"))):
    """
    Minimal admin-only endpoint to verify RBAC wiring.
    """
    return {"detail": "admin-ok"}
