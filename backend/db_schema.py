"""
Lightweight schema patches for existing databases.

SQLAlchemy create_all does not add new columns to existing tables; this module
aligns older installs when new nullable/default columns are introduced.
"""

from sqlalchemy import inspect, text

from .database import engine


def ensure_users_role_column() -> None:
    inspector = inspect(engine)
    if "users" not in inspector.get_table_names():
        return
    columns = {col["name"] for col in inspector.get_columns("users")}
    if "role" in columns:
        return

    stmt = "ALTER TABLE users ADD COLUMN role VARCHAR NOT NULL DEFAULT 'user'"
    with engine.begin() as conn:
        conn.execute(text(stmt))
