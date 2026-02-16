"""
Database abstraction layer for Anna AI - Phase 3

Provides:
- Database connection management
- Connection pooling
- Session management
- Query helpers
- Transaction support
"""

import os
from contextlib import contextmanager
from typing import Optional, Dict, Any, List, Generator
from pathlib import Path
import logging

from sqlalchemy import create_engine, event, pool, text
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.engine import Engine
from sqlalchemy.pool import Pool

# Create base class for all models
Base = declarative_base()

logger = logging.getLogger(__name__)


class DatabaseConfig:
    """Database configuration."""

    def __init__(self):
        """Initialize database configuration from environment."""
        self.database_url = os.getenv(
            "DATABASE_URL",
            "postgresql://anna:password@localhost:5432/anna_ai"
        )
        self.pool_size = int(os.getenv("DB_POOL_SIZE", "10"))
        self.max_overflow = int(os.getenv("DB_MAX_OVERFLOW", "20"))
        self.pool_recycle = int(os.getenv("DB_POOL_RECYCLE", "3600"))
        self.echo = os.getenv("DB_ECHO", "false").lower() == "true"
        self.create_tables = os.getenv("DB_CREATE_TABLES", "true").lower() == "true"

    def validate(self) -> bool:
        """Validate database configuration."""
        if not self.database_url:
            logger.error("DATABASE_URL not set")
            return False

        if "postgresql" not in self.database_url and "mysql" not in self.database_url and "sqlite" not in self.database_url:
            logger.error("Only PostgreSQL, MySQL, and SQLite are supported")
            return False

        return True


class Database:
    """Database connection manager."""

    _instance: Optional["Database"] = None

    def __new__(cls) -> "Database":
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False

        return cls._instance

    def __init__(self):
        """Initialize database manager."""
        if self._initialized:
            return

        self.config = DatabaseConfig()

        if not self.config.validate():
            raise ValueError("Invalid database configuration")

        # Create engine
        self.engine = self._create_engine()

        # Create session factory
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
        )

        # Register event listeners
        self._setup_event_listeners()

        db_info = self.config.database_url.split("@")[-1] if "@" in self.config.database_url else self.config.database_url
        logger.info(f"Database initialized: {db_info}")

        self._initialized = True

    def _create_engine(self) -> Engine:
        """Create SQLAlchemy engine with connection pooling."""
        if "sqlite" in self.config.database_url:
            # SQLite: StaticPool, no pool_size/max_overflow
            kwargs = {
                "echo": self.config.echo,
                "poolclass": pool.StaticPool,
            }
        else:
            kwargs = {
                "echo": self.config.echo,
                "pool_size": self.config.pool_size,
                "max_overflow": self.config.max_overflow,
                "pool_recycle": self.config.pool_recycle,
                "poolclass": pool.QueuePool,
            }

        engine = create_engine(self.config.database_url, **kwargs)

        return engine

    def _setup_event_listeners(self) -> None:
        """Setup SQLAlchemy event listeners."""
        # Log connections
        @event.listens_for(Pool, "connect")
        def receive_connect(dbapi_conn, connection_record):
            logger.debug("Database connection established")

        @event.listens_for(Pool, "close")
        def receive_close(dbapi_conn, connection_record):
            logger.debug("Database connection closed")

        @event.listens_for(Pool, "detach")
        def receive_detach(dbapi_conn, connection_record):
            logger.debug("Database connection detached")

    def get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """
        Provide a transactional scope for database operations.

        Usage:
            with db.session_scope() as session:
                session.add(obj)
                session.commit()
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()

    def create_tables(self) -> None:
        """Create all tables in the database."""
        if self.config.create_tables:
            logger.info("Creating database tables...")
            Base.metadata.create_all(self.engine)
            logger.info("Database tables created")

    def drop_tables(self) -> None:
        """Drop all tables (for testing/cleanup)."""
        logger.warning("Dropping all database tables...")
        Base.metadata.drop_all(self.engine)
        logger.info("Database tables dropped")

    def health_check(self) -> bool:
        """
        Check database connection health.

        Returns:
            True if database is accessible, False otherwise
        """
        try:
            with self.session_scope() as session:
                session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False

    def get_engine(self) -> Engine:
        """Get the SQLAlchemy engine."""
        return self.engine

    def dispose_pool(self) -> None:
        """Dispose of the connection pool (useful for testing)."""
        self.engine.dispose()

    def close(self) -> None:
        """Close all connections."""
        self.engine.dispose()
        logger.info("Database connections closed")


class BaseModel:
    """Base class for all database models."""

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

    def update(self, **kwargs) -> None:
        """Update model attributes."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def __repr__(self) -> str:
        """String representation."""
        attrs = ", ".join(
            f"{col.name}={getattr(self, col.name)!r}"
            for col in self.__table__.columns
        )
        return f"<{self.__class__.__name__}({attrs})>"


# Query helper functions
def get_or_create(session: Session, model: type, **kwargs) -> tuple:
    """
    Get an existing object or create a new one.

    Returns:
        Tuple of (object, created) where created is True if new
    """
    instance = session.query(model).filter_by(**kwargs).first()

    if instance:
        return instance, False

    instance = model(**kwargs)
    session.add(instance)
    return instance, True


def paginate(query, page: int = 1, per_page: int = 20):
    """
    Paginate query results.

    Args:
        query: SQLAlchemy query object
        page: Page number (1-indexed)
        per_page: Results per page

    Returns:
        Tuple of (items, total, pages)
    """
    total = query.count()
    pages = (total + per_page - 1) // per_page

    items = query.offset((page - 1) * per_page).limit(per_page).all()

    return items, total, pages


def bulk_insert(session: Session, objects: List[Any]) -> int:
    """
    Insert multiple objects efficiently.

    Args:
        session: Database session
        objects: List of objects to insert

    Returns:
        Number of objects inserted
    """
    session.bulk_save_objects(objects)
    session.commit()
    return len(objects)


def bulk_update(session: Session, objects: List[Any]) -> int:
    """
    Update multiple objects efficiently.

    Args:
        session: Database session
        objects: List of objects to update

    Returns:
        Number of objects updated
    """
    session.bulk_update_mappings(objects)
    session.commit()
    return len(objects)
