"""Alembic environment configuration for Anna AI Phase 3."""

import os
import sys
from pathlib import Path

# Add project root to path for BASE imports
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

config = context.config

# Use DATABASE_URL from environment
database_url = os.getenv("DATABASE_URL", "postgresql://anna:password@localhost:5432/anna_ai")
config.set_main_option("sqlalchemy.url", database_url)

try:
    fileConfig(config.config_file_name)
except Exception:
    pass

from BASE.database import Base
from BASE.models import *  # noqa: F401, F403 - Import all models for autogenerate
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
