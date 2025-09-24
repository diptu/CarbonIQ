import asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from ima_service.main import app
from ima_service.app.db.base import Base  # contains your models
from ima_service.app import db
from ima_service.app.api import deps

# -------------------------------
# Setup in-memory SQLite database
# -------------------------------
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine_test = create_async_engine(TEST_DATABASE_URL, future=True, echo=False)
async_session_test = sessionmaker(
    engine_test, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_db():
    """Create tables before tests, drop after."""
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session():
    """Provide a fresh DB session for a test."""
    async with async_session_test() as session:
        try:
            yield session
        finally:
            await session.rollback()


@pytest.fixture(autouse=True)
def override_get_db(db_session: AsyncSession):
    """Override FastAPI's get_db + async_session_maker with test session."""

    async def _override():
        yield db_session

    # Override FastAPI dependency
    app.dependency_overrides[deps.get_db] = _override

    # Override global session maker (important!)
    db.session.async_session_maker = async_session_test

    yield
    app.dependency_overrides.clear()


@pytest.fixture
async def async_client():
    """FastAPI async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
