# migrations/env.py
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

from app.core.config import get_settings

# Import all models here so Alembic can see them
from app.db.base_class import Base
from app.models import *

# Import any other models here
# from app.models.other_model import OtherModel

# Alembic Config object
config = context.config

# Logging setup
fileConfig(config.config_file_name)

# Use synchronous DB URL for Alembic
settings = get_settings()
DATABASE_URL = os.getenv(
    "SQLALCHEMY_DATABASE_URL_SYNC"
) or settings.DATABASE_URL.replace("+asyncpg", "")

# Metadata for autogenerate
target_metadata = Base.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        url=DATABASE_URL,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            render_as_batch=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
