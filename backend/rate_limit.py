from slowapi import Limiter
from slowapi.util import get_remote_address

from .config import RATE_LIMIT_DEFAULT

# Shared limiter instance; attached to FastAPI app.state in main.py
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[RATE_LIMIT_DEFAULT],
    # FastAPI often returns plain dicts from sync endpoints; SlowAPI header
    # injection requires a Starlette Response instance (see slowapi # compatibility).
    headers_enabled=False,
)
