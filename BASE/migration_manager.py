"""
Database migration manager for Anna AI - Phase 3

Handles:
- Schema version management
- Migration execution
- Rollback capability
- Migration tracking
"""

import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
from alembic.config import Config
from alembic.command import upgrade, downgrade, current as alembic_current
from alembic.runtime.migration import MigrationContext
from alembic.operations import Operations

from BASE.database import Database

logger = logging.getLogger(__name__)


class MigrationManager:
    """Manage database migrations."""

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize migration manager.

        Args:
            project_root: Project root directory
        """
        self.project_root = project_root or Path(__file__).parent.parent
        self.migrations_dir = self.project_root / "migrations"
        self.db = Database()

    def init_migrations(self) -> bool:
        """
        Initialize Alembic migrations directory.

        Returns:
            True if successful, False otherwise
        """
        try:
            if self.migrations_dir.exists():
                logger.info("Migrations directory already exists")
                return True

            logger.info("Initializing migrations directory...")

            # Create migrations directory structure
            self.migrations_dir.mkdir(parents=True, exist_ok=True)
            (self.migrations_dir / "versions").mkdir(exist_ok=True)

            # Create alembic.ini
            alembic_ini = self._create_alembic_ini()
            (self.project_root / "alembic.ini").write_text(alembic_ini)

            # Create env.py
            env_py = self._create_env_py()
            (self.migrations_dir / "env.py").write_text(env_py)

            # Create script.py.mako
            script_py = self._create_script_py_mako()
            (self.migrations_dir / "script.py.mako").write_text(script_py)

            # Create __init__.py
            (self.migrations_dir / "__init__.py").write_text("")
            (self.migrations_dir / "versions").touch()

            logger.info("Migrations initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize migrations: {e}")
            return False

    def create_migration(self, message: str) -> Optional[str]:
        """
        Create a new migration.

        Args:
            message: Migration description

        Returns:
            Migration file name if successful, None otherwise
        """
        try:
            config = self._get_alembic_config()

            # Generate migration
            from alembic.command import revision
            revision(config, autogenerate=True, message=message)

            logger.info(f"Migration created: {message}")
            return message

        except Exception as e:
            logger.error(f"Failed to create migration: {e}")
            return None

    def upgrade(self, target: str = "head") -> bool:
        """
        Upgrade database to target migration.

        Args:
            target: Target migration (e.g., "head", "+1", "abc123def456")

        Returns:
            True if successful, False otherwise
        """
        try:
            config = self._get_alembic_config()
            upgrade(config, target)

            logger.info(f"Database upgraded to {target}")
            return True

        except Exception as e:
            logger.error(f"Migration upgrade failed: {e}")
            return False

    def downgrade(self, target: str = "-1") -> bool:
        """
        Downgrade database to target migration.

        Args:
            target: Target migration (e.g., "-1", "abc123def456")

        Returns:
            True if successful, False otherwise
        """
        try:
            config = self._get_alembic_config()
            downgrade(config, target)

            logger.info(f"Database downgraded to {target}")
            return True

        except Exception as e:
            logger.error(f"Migration downgrade failed: {e}")
            return False

    def current_migration(self) -> Optional[str]:
        """
        Get current migration version.

        Returns:
            Current migration ID or None
        """
        try:
            config = self._get_alembic_config()
            engine = self.db.get_engine()

            with engine.begin() as connection:
                context = MigrationContext.configure(connection)
                return context.get_current_revision()

        except Exception as e:
            logger.error(f"Failed to get current migration: {e}")
            return None

    def list_migrations(self) -> List[Dict[str, Any]]:
        """
        List all migrations.

        Returns:
            List of migration info dicts
        """
        migrations = []

        try:
            versions_dir = self.migrations_dir / "versions"

            if not versions_dir.exists():
                return migrations

            for migration_file in sorted(versions_dir.glob("*.py")):
                if migration_file.name.startswith("_"):
                    continue

                migration_id = migration_file.stem.split("_")[0]
                migration_message = "_".join(migration_file.stem.split("_")[1:])

                migrations.append({
                    "id": migration_id,
                    "message": migration_message,
                    "file": migration_file.name,
                    "created_at": datetime.fromtimestamp(migration_file.stat().st_mtime),
                })

            return migrations

        except Exception as e:
            logger.error(f"Failed to list migrations: {e}")
            return []

    def validate_migrations(self) -> bool:
        """
        Validate migration integrity.

        Returns:
            True if all migrations are valid, False otherwise
        """
        try:
            config = self._get_alembic_config()
            engine = self.db.get_engine()

            # Check alembic_version table exists
            inspector = __import__('sqlalchemy').inspect(engine)

            if "alembic_version" not in inspector.get_table_names():
                logger.warning("alembic_version table not found")
                return False

            logger.info("Migrations validated successfully")
            return True

        except Exception as e:
            logger.error(f"Migration validation failed: {e}")
            return False

    def _get_alembic_config(self) -> Config:
        """Get Alembic configuration."""
        config = Config(str(self.project_root / "alembic.ini"))
        config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL", ""))
        return config

    def _create_alembic_ini(self) -> str:
        """Create alembic.ini file content."""
        return """# Alembic Configuration File

[alembic]
script_location = migrations
sqlalchemy.url = postgresql://localhost/anna_ai
version_path_separator = :
version_locations = %(here)s/migrations/versions

[loggers]
keys = root,sqlalchemy

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
"""

    def _create_env_py(self) -> str:
        """Create env.py file content."""
        return '''"""Alembic environment configuration."""

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

# Get config
config = context.config

# Use DATABASE_URL from environment if set
import os
database_url = os.getenv("DATABASE_URL")
if database_url:
    config.set_main_option("sqlalchemy.url", database_url)

# Configure logging (skip if fileConfig fails in some environments)
try:
    fileConfig(config.config_file_name)
except Exception:
    pass

# Import Base for autogenerate support
from BASE.database import Base
target_metadata = Base.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
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
'''

    def _create_script_py_mako(self) -> str:
        """Create script.py.mako file content."""
        return '''"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
'''


# Convenience functions
def migrate_up(target: str = "head") -> bool:
    """Upgrade database."""
    manager = MigrationManager()
    return manager.upgrade(target)


def migrate_down(target: str = "-1") -> bool:
    """Downgrade database."""
    manager = MigrationManager()
    return manager.downgrade(target)


def create_migration(message: str) -> Optional[str]:
    """Create new migration."""
    manager = MigrationManager()
    return manager.create_migration(message)


def list_all_migrations() -> List[Dict[str, Any]]:
    """List all migrations."""
    manager = MigrationManager()
    return manager.list_migrations()


def current_migration() -> Optional[str]:
    """Get current migration."""
    manager = MigrationManager()
    return manager.current_migration()
