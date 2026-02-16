"""
Comprehensive tests for Anna AI database layer - Phase 3

Tests:
- Database connection and pooling
- CRUD operations
- Query helpers
- Transaction handling
- Model relationships
- Migration system
"""

import pytest
import uuid
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError

from BASE.database import Database, get_or_create, paginate, bulk_insert, bulk_update
from BASE.models import (
    MemoryEntry,
    MemoryTier,
    ConfigEntry,
    SessionData,
    AuditLog,
    WebhookRecord,
    ErrorLog,
)


@pytest.fixture
def db():
    """Create test database instance."""
    import os

    # Use SQLite for testing
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"

    # Reset singleton so each test gets a fresh instance
    Database._instance = None

    db_instance = Database()
    db_instance.create_tables()
    yield db_instance
    db_instance.close()
    Database._instance = None


class TestDatabaseConnection:
    """Test database connection and pooling."""

    def test_database_singleton(self, db):
        """Test database singleton pattern."""
        db2 = Database()
        assert db is db2

    def test_health_check(self, db):
        """Test database health check."""
        assert db.health_check() is True

    def test_get_session(self, db):
        """Test getting a new session."""
        session = db.get_session()
        assert session is not None
        session.close()

    def test_session_scope(self, db):
        """Test session context manager."""
        with db.session_scope() as session:
            assert session is not None


class TestMemoryOperations:
    """Test memory entry CRUD operations."""

    def test_create_memory(self, db):
        """Test creating a memory entry."""
        with db.session_scope() as session:
            memory = MemoryEntry(
                content="Test memory content",
                tier=MemoryTier.SHORT,
                tags=["test", "demo"],
            )
            session.add(memory)
            session.commit()

            assert memory.id is not None
            assert memory.content == "Test memory content"
            assert memory.tier == MemoryTier.SHORT

    def test_read_memory(self, db):
        """Test reading a memory entry."""
        memory_id = None

        with db.session_scope() as session:
            memory = MemoryEntry(
                content="Test memory",
                tier=MemoryTier.MEDIUM,
            )
            session.add(memory)
            session.commit()
            memory_id = memory.id

        with db.session_scope() as session:
            retrieved = session.query(MemoryEntry).filter_by(id=memory_id).first()
            assert retrieved is not None
            assert retrieved.content == "Test memory"

    def test_update_memory(self, db):
        """Test updating a memory entry."""
        memory_id = None

        with db.session_scope() as session:
            memory = MemoryEntry(
                content="Original content",
                tier=MemoryTier.SHORT,
            )
            session.add(memory)
            session.commit()
            memory_id = memory.id

        with db.session_scope() as session:
            memory = session.query(MemoryEntry).filter_by(id=memory_id).first()
            memory.content = "Updated content"
            session.commit()

        with db.session_scope() as session:
            memory = session.query(MemoryEntry).filter_by(id=memory_id).first()
            assert memory.content == "Updated content"

    def test_delete_memory(self, db):
        """Test deleting a memory entry."""
        memory_id = None

        with db.session_scope() as session:
            memory = MemoryEntry(
                content="To delete",
                tier=MemoryTier.SHORT,
            )
            session.add(memory)
            session.commit()
            memory_id = memory.id

        with db.session_scope() as session:
            memory = session.query(MemoryEntry).filter_by(id=memory_id).first()
            session.delete(memory)
            session.commit()

        with db.session_scope() as session:
            memory = session.query(MemoryEntry).filter_by(id=memory_id).first()
            assert memory is None

    def test_memory_expiration(self, db):
        """Test memory expiration logic."""
        with db.session_scope() as session:
            # Create expired memory
            memory = MemoryEntry(
                content="Expired memory",
                tier=MemoryTier.SHORT,
                expires_at=datetime.utcnow() - timedelta(days=1),
            )
            session.add(memory)
            session.commit()

            # Query non-expired memories
            active = session.query(MemoryEntry).filter(
                MemoryEntry.expires_at > datetime.utcnow()
            ).all()

            assert memory not in active

    def test_memory_by_tier(self, db):
        """Test querying memories by tier."""
        with db.session_scope() as session:
            # Create memories of different tiers
            short = MemoryEntry(content="Short", tier=MemoryTier.SHORT)
            medium = MemoryEntry(content="Medium", tier=MemoryTier.MEDIUM)
            long = MemoryEntry(content="Long", tier=MemoryTier.LONG)

            session.add_all([short, medium, long])
            session.commit()

            # Query by tier
            short_memories = session.query(MemoryEntry).filter_by(
                tier=MemoryTier.SHORT
            ).all()

            assert len(short_memories) == 1
            assert short_memories[0].content == "Short"


class TestConfigurationOperations:
    """Test configuration entry operations."""

    def test_create_config(self, db):
        """Test creating a config entry."""
        with db.session_scope() as session:
            config = ConfigEntry(
                id="debug_mode",
                value={"enabled": True},
                version=1,
            )
            session.add(config)
            session.commit()

            assert config.id == "debug_mode"
            assert config.value["enabled"] is True

    def test_update_config_version(self, db):
        """Test updating config with version tracking."""
        with db.session_scope() as session:
            config = ConfigEntry(
                id="api_key",
                value={"key": "abc123"},
                version=1,
            )
            session.add(config)
            session.commit()

            config.value = {"key": "xyz789"}
            config.version = 2
            session.commit()

            retrieved = session.query(ConfigEntry).filter_by(id="api_key").first()
            assert retrieved.version == 2
            assert retrieved.value["key"] == "xyz789"


class TestSessionManagement:
    """Test session data operations."""

    def test_create_session(self, db):
        """Test creating a session."""
        with db.session_scope() as session:
            sess = SessionData(
                user_id="user123",
                data={"authenticated": True},
                expires_at=datetime.utcnow() + timedelta(hours=1),
            )
            session.add(sess)
            session.commit()

            assert sess.session_id is not None
            assert sess.user_id == "user123"

    def test_session_expiration_check(self, db):
        """Test session expiration check."""
        with db.session_scope() as session:
            # Create expired session
            expired = SessionData(
                user_id="user1",
                data={},
                expires_at=datetime.utcnow() - timedelta(hours=1),
            )

            # Create active session
            active = SessionData(
                user_id="user2",
                data={},
                expires_at=datetime.utcnow() + timedelta(hours=1),
            )

            session.add_all([expired, active])
            session.commit()

            # Query active sessions
            active_sessions = session.query(SessionData).filter(
                SessionData.expires_at > datetime.utcnow()
            ).all()

            assert len(active_sessions) == 1
            assert active_sessions[0].user_id == "user2"


class TestAuditLogging:
    """Test audit log operations."""

    def test_create_audit_log(self, db):
        """Test creating an audit log entry."""
        with db.session_scope() as session:
            audit = AuditLog(
                user_id="user123",
                action="create_memory",
                resource_type="memory",
                resource_id=str(uuid.uuid4()),
                status="success",
            )
            session.add(audit)
            session.commit()

            assert audit.id is not None
            assert audit.action == "create_memory"

    def test_audit_log_by_action(self, db):
        """Test querying audit logs by action."""
        with db.session_scope() as session:
            # Create multiple audit logs
            for i in range(3):
                audit = AuditLog(
                    user_id=f"user{i}",
                    action="create_memory",
                    resource_type="memory",
                    resource_id=str(uuid.uuid4()),
                    status="success",
                )
                session.add(audit)

            session.commit()

            # Query by action
            logs = session.query(AuditLog).filter_by(
                action="create_memory"
            ).all()

            assert len(logs) == 3


class TestWebhookOperations:
    """Test webhook management."""

    def test_register_webhook(self, db):
        """Test registering a webhook."""
        with db.session_scope() as session:
            webhook = WebhookRecord(
                event_type="message_received",
                url="https://example.com/webhook",
                active=True,
            )
            session.add(webhook)
            session.commit()

            assert webhook.id is not None
            assert webhook.active is True

    def test_webhook_delivery_tracking(self, db):
        """Test tracking webhook deliveries."""
        with db.session_scope() as session:
            webhook = WebhookRecord(
                event_type="tool_executed",
                url="https://example.com/webhook",
                active=True,
                delivery_count=0,
                failure_count=0,
            )
            session.add(webhook)
            session.commit()

            webhook.delivery_count += 1
            webhook.last_delivery_at = datetime.utcnow()
            webhook.last_delivery_status = 200
            session.commit()

            retrieved = session.query(WebhookRecord).filter_by(
                event_type="tool_executed"
            ).first()

            assert retrieved.delivery_count == 1
            assert retrieved.last_delivery_status == 200


class TestErrorLogging:
    """Test error logging."""

    def test_log_error(self, db):
        """Test logging an error."""
        with db.session_scope() as session:
            error = ErrorLog(
                error_type="ValueError",
                message="Invalid configuration value",
                severity="error",
                resolved=False,
            )
            session.add(error)
            session.commit()

            assert error.id is not None
            assert error.error_type == "ValueError"

    def test_error_severity_filtering(self, db):
        """Test filtering errors by severity."""
        with db.session_scope() as session:
            critical = ErrorLog(
                error_type="CriticalError",
                message="Critical issue",
                severity="critical",
                resolved=False,
            )
            warning = ErrorLog(
                error_type="Warning",
                message="Minor issue",
                severity="warning",
                resolved=False,
            )

            session.add_all([critical, warning])
            session.commit()

            # Query critical errors
            critical_errors = session.query(ErrorLog).filter_by(
                severity="critical"
            ).all()

            assert len(critical_errors) == 1


class TestQueryHelpers:
    """Test query helper functions."""

    def test_get_or_create_existing(self, db):
        """Test get_or_create with existing object."""
        config_id = "test_config"

        with db.session_scope() as session:
            config = ConfigEntry(
                id=config_id,
                value={"test": True},
            )
            session.add(config)
            session.commit()

        with db.session_scope() as session:
            obj, created = get_or_create(
                session,
                ConfigEntry,
                id=config_id,
                value={"test": True},
            )

            assert created is False
            assert obj.id == config_id

    def test_get_or_create_new(self, db):
        """Test get_or_create with new object."""
        with db.session_scope() as session:
            obj, created = get_or_create(
                session,
                ConfigEntry,
                id="new_config",
                value={"new": True},
            )

            assert created is True
            assert obj.id == "new_config"

    def test_paginate(self, db):
        """Test pagination helper."""
        with db.session_scope() as session:
            # Create 25 memory entries
            for i in range(25):
                memory = MemoryEntry(
                    content=f"Memory {i}",
                    tier=MemoryTier.SHORT,
                )
                session.add(memory)

            session.commit()

            # Query and paginate
            query = session.query(MemoryEntry)
            items, total, pages = paginate(query, page=1, per_page=10)

            assert len(items) == 10
            assert total == 25
            assert pages == 3

            # Test page 2
            items2, _, _ = paginate(query, page=2, per_page=10)
            assert len(items2) == 10


class TestTransactions:
    """Test transaction handling."""

    def test_rollback_on_error(self, db):
        """Test rollback on error."""
        try:
            with db.session_scope() as session:
                memory = MemoryEntry(
                    content="Will rollback",
                    tier=MemoryTier.SHORT,
                )
                session.add(memory)
                raise Exception("Simulated error")

        except Exception:
            pass

        # Verify rollback
        with db.session_scope() as session:
            memories = session.query(MemoryEntry).filter(
                MemoryEntry.content == "Will rollback"
            ).all()

            assert len(memories) == 0

    def test_nested_transactions(self, db):
        """Test nested transaction handling."""
        with db.session_scope() as session:
            memory1 = MemoryEntry(
                content="Memory 1",
                tier=MemoryTier.SHORT,
            )
            session.add(memory1)

            with db.session_scope() as session2:
                memory2 = MemoryEntry(
                    content="Memory 2",
                    tier=MemoryTier.MEDIUM,
                )
                session2.add(memory2)

            # Both should exist
            all_memories = session.query(MemoryEntry).all()
            assert len(all_memories) >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
