"""Database session and test connection for Auth service."""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from auth_service.app.core.config import settings

# -------------------------------
# Database engine & session with connection pool
# -------------------------------
engine = create_engine(
    settings.DATABASE_URL,  # type: ignore[arg-type]
    pool_size=10,  # Number of connections to keep in the pool
    max_overflow=20,  # Max connections to allow beyond pool_size
    pool_timeout=30,  # Wait time (seconds) for getting a connection
    pool_recycle=1800,  # Recycle connections after 30 minutes
    pool_pre_ping=True,  # Check if connection is alive before using
)

session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Yield a database session and close it after use."""
    db = session_local()
    try:
        yield db
    finally:
        db.close()


# # -------------------------------
# # Test DB connection
# # -------------------------------
# def test_db_connection():
#     """Test if the database is reachable."""
#     try:
#         with engine.connect() as connection:
#             result = connection.execute(text("SELECT 1"))
#             print("Database connection successful!", result.scalar())
#     except SQLAlchemyError as e:
#         print("Database connection failed:", e)


# if __name__ == "__main__":
#     test_db_connection()
