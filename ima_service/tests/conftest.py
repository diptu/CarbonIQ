# tests/conftest.py
import pytest
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport

from ima_service.app.main import app
from ima_service.app.db.session import async_session, get_db, engine
from ima_service.app.db.base import Base  # your declarative base


# Automatically create tables in test DB
@pytest.fixture(scope="session", autouse=True)
async def prepare_test_db():
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Optionally drop tables after tests
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# Override the FastAPI dependency to use test DB
@pytest.fixture
async def async_client():
    async def _get_test_db():
        async with async_session() as session:
            yield session

    app.dependency_overrides[get_db] = _get_test_db

    # Use ASGITransport instead of app= argument
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
