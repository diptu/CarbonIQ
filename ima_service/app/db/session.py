from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from ..core.config import get_settings

settings = get_settings()

# -------------------------
# Async Engine
# -------------------------
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
)

# -------------------------
# Async session factory
# -------------------------
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# -------------------------
# FastAPI Dependency
# -------------------------
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide a transactional scope around a series of operations.

    Yields
    ------
    AsyncSession
        SQLAlchemy async session instance.
    """
    async with async_session() as session:
        yield session
