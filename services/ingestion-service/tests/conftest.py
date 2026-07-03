"""Shared pytest fixtures.

Tests run against an in-memory SQLite database (via aiosqlite) and a
fake in-process object store, so the full suite runs with no external
services (no Postgres/RabbitMQ/Redis/MinIO required).
"""

import uuid
from collections.abc import AsyncGenerator, Iterator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

from app.core.security import AuthContext, get_current_auth
from app.db import Base, get_db
from app.main import app
from app.storage.s3 import get_object_storage


class FakeObjectStorage:
    """In-memory stand-in for ObjectStorage, keyed the same way S3 is."""

    def __init__(self) -> None:
        self._objects: dict[str, bytes] = {}
        self.bucket = "test-bucket"

    def ensure_bucket(self) -> None:
        pass

    def put_object(self, key, body, content_type) -> None:  # noqa: ANN001
        self._objects[key] = body.read()

    def get_object_bytes(self, key: str) -> bytes:
        return self._objects[key]

    def delete_object(self, key: str) -> None:
        self._objects.pop(key, None)

    def presigned_get_url(self, key: str, expires_in: int = 900) -> str:
        return f"https://fake-storage.local/{self.bucket}/{key}?expires_in={expires_in}"


@pytest.fixture
def fake_storage() -> FakeObjectStorage:
    return FakeObjectStorage()


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        yield session

    await engine.dispose()


@pytest.fixture
def tenant_id() -> str:
    return str(uuid.uuid4())


@pytest.fixture
def user_id() -> str:
    return str(uuid.uuid4())


@pytest.fixture
def auth_context(tenant_id: str, user_id: str) -> AuthContext:
    return AuthContext(
        user_id=user_id,
        tenant_id=tenant_id,
        roles=["tenant_admin"],
        permissions=["manage_ingestion"],
    )


@pytest.fixture
def override_dependencies(
    db_session: AsyncSession,
    fake_storage: FakeObjectStorage,
    auth_context: AuthContext,
) -> Iterator[None]:
    async def _get_db_override() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = _get_db_override
    app.dependency_overrides[get_object_storage] = lambda: fake_storage
    app.dependency_overrides[get_current_auth] = lambda: auth_context

    yield

    app.dependency_overrides.clear()


@pytest.fixture
async def client(override_dependencies: None) -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac
