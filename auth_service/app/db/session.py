"""Database session and test connection for Auth service."""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

# -------------------------------
# Database engine & session
# -------------------------------
engine = create_engine(settings.DATABASE_URL) # type: ignore[arg-type]
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
