import os
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Configure env before importing the FastAPI app (engine binds at import time).
_db_fd, _db_path = tempfile.mkstemp(suffix=".sqlite")
os.close(_db_fd)
os.environ["DATABASE_URL"] = f"sqlite:///{Path(_db_path).as_posix()}"
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-ci-only-please-change")
os.environ.setdefault("REFRESH_SECRET_KEY", "test-refresh-secret-key-for-ci-only-change")
os.environ.setdefault("ADMIN_EMAILS", "admin@test.com")
os.environ.setdefault("APPLICATIONINSIGHTS_CONNECTION_STRING", "")

from backend.main import app  # noqa: E402


@pytest.fixture(scope="session")
def client() -> TestClient:
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c


@pytest.fixture(scope="session", autouse=True)
def _cleanup_tmp_db():
    yield
    try:
        Path(_db_path).unlink(missing_ok=True)
    except OSError:
        pass
