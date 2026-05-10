from sqlalchemy import text

from . import models
from .database import engine
from .db_schema import ensure_users_role_column


def init_database() -> None:
    """
    Initialize schema safely.

    With multi-worker Gunicorn on PostgreSQL, concurrent create_all() calls can race.
    We serialize startup DDL using a PostgreSQL advisory lock.
    """
    if engine.dialect.name == "postgresql":
        with engine.begin() as conn:
            conn.execute(text("SELECT pg_advisory_lock(93827123456789)"))
            try:
                models.User.metadata.create_all(bind=conn)
                models.Task.metadata.create_all(bind=conn)
                ensure_users_role_column()
            finally:
                conn.execute(text("SELECT pg_advisory_unlock(93827123456789)"))
        return

    models.User.metadata.create_all(bind=engine)
    models.Task.metadata.create_all(bind=engine)
    ensure_users_role_column()
