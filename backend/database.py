from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite URL for SQLAlchemy. The "check_same_thread" option is needed for SQLite + FastAPI.
SQLALCHEMY_DATABASE_URL = "sqlite:///./smart_task_manager.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Dependency that provides a database session to path operations.
    It makes sure the session is closed after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

