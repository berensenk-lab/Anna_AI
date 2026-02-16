"""
Database models for Anna AI - Phase 3

Models:
- MemoryEntry: Store agent memories
- ConfigEntry: Store configuration
- SessionData: User sessions
- AuditLog: Audit trail
- WebhookRecord: Webhook tracking
"""

from datetime import datetime
from typing import Optional
import uuid

from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    Integer,
    Float,
    Boolean,
    JSON,
    LargeBinary,
    Index,
    TypeDecorator,
    CHAR,
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import relationship

from BASE.database import Base, BaseModel
import enum


# Cross-dialect UUID: native UUID on PostgreSQL, CHAR(36) on SQLite
class GUID(TypeDecorator):
    """Platform-independent UUID type."""

    impl = CHAR(36)
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == "postgresql":
            return value
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(value)


# JSON type that uses JSONB on PostgreSQL, JSON on SQLite
def JsonType():
    """Platform-independent JSON type (JSONB on PostgreSQL, JSON on SQLite)."""
    return JSON().with_variant(JSONB(), "postgresql")


class MemoryTier(str, enum.Enum):
    """Memory tier enumeration."""

    SHORT = "short"      # Recent interactions
    MEDIUM = "medium"    # Earlier today
    LONG = "long"        # Past days/weeks
    BASE = "base"        # Permanent knowledge


class MemoryEntry(Base, BaseModel):
    """Store agent memories."""

    __tablename__ = "memory_entries"

    # Primary key
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)

    # Content
    content = Column(Text, nullable=False, index=True)
    summary = Column(Text, nullable=True)

    # Metadata
    tier = Column(SQLEnum(MemoryTier), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime, nullable=True, index=True)

    # Embeddings (for vector search)
    embedding = Column(LargeBinary, nullable=True)
    embedding_model = Column(String(100), nullable=True)

    # Tags and metadata
    tags = Column(JsonType(), nullable=True)
    metadata_ = Column("metadata", JsonType(), nullable=True)

    # Relationships
    related_ids = Column(JsonType(), nullable=True)  # IDs of related memories

    # Tracking
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    accessed_at = Column(DateTime, nullable=True)

    # Indexes (postgresql_using="gin" for JSON on PostgreSQL only)
    __table_args__ = (
        Index("idx_memory_tier_timestamp", "tier", "timestamp"),
        Index("idx_memory_tags", "tags", postgresql_using="gin"),
        Index("idx_memory_expires", "expires_at"),
    )

    def __repr__(self) -> str:
        return f"<MemoryEntry(id={self.id}, tier={self.tier}, content_len={len(self.content)})>"


class ConfigEntry(Base, BaseModel):
    """Store configuration entries."""

    __tablename__ = "config_entries"

    # Primary key
    id = Column(String(255), primary_key=True)

    # Value
    value = Column(JsonType(), nullable=False)

    # Versioning
    version = Column(Integer, nullable=False, default=1)

    # Metadata
    description = Column(Text, nullable=True)
    type_hint = Column(String(100), nullable=True)

    # Tracking
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    changed_by = Column(String(255), nullable=True)

    # Indexes
    __table_args__ = (
        Index("idx_config_updated", "updated_at"),
    )

    def __repr__(self) -> str:
        return f"<ConfigEntry(id={self.id}, version={self.version})>"


class SessionData(Base, BaseModel):
    """User session data."""

    __tablename__ = "sessions"

    # Primary key
    session_id = Column(GUID(), primary_key=True, default=uuid.uuid4)

    # Session info
    user_id = Column(String(255), nullable=True, index=True)
    api_key_hash = Column(String(255), nullable=True, index=True)

    # Session data
    data = Column(JsonType(), nullable=False)
    session_metadata = Column("metadata", JsonType(), nullable=True)

    # Lifecycle
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_activity = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False, index=True)

    # State
    is_active = Column(Boolean, nullable=False, default=True)

    # Indexes
    __table_args__ = (
        Index("idx_session_expires", "expires_at"),
        Index("idx_session_active", "is_active"),
        Index("idx_session_user", "user_id"),
    )

    def is_expired(self) -> bool:
        """Check if session is expired."""
        return datetime.utcnow() > self.expires_at

    def __repr__(self) -> str:
        return f"<SessionData(session_id={self.session_id}, user_id={self.user_id})>"


class AuditLog(Base, BaseModel):
    """Audit trail for all operations."""

    __tablename__ = "audit_logs"

    # Primary key
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)

    # User info
    user_id = Column(String(255), nullable=True, index=True)
    api_key_hash = Column(String(255), nullable=True)

    # Action info
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(100), nullable=False, index=True)
    resource_id = Column(String(255), nullable=True)

    # Details
    details = Column(JsonType(), nullable=True)
    changes = Column(JsonType(), nullable=True)

    # Result
    status = Column(String(50), nullable=False, index=True)  # success, error, denied
    error_message = Column(Text, nullable=True)

    # Tracking
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    duration_ms = Column(Integer, nullable=True)
    ip_address = Column(String(50), nullable=True)

    # Indexes
    __table_args__ = (
        Index("idx_audit_user_timestamp", "user_id", "timestamp"),
        Index("idx_audit_action_timestamp", "action", "timestamp"),
        Index("idx_audit_resource", "resource_type", "resource_id"),
    )

    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, action={self.action}, status={self.status})>"


class WebhookRecord(Base, BaseModel):
    """Track webhook registrations and deliveries."""

    __tablename__ = "webhooks"

    # Primary key
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)

    # Webhook info
    event_type = Column(String(100), nullable=False, index=True)
    url = Column(String(2048), nullable=False)
    active = Column(Boolean, nullable=False, default=True)

    # Delivery tracking
    last_delivery_at = Column(DateTime, nullable=True)
    last_delivery_status = Column(Integer, nullable=True)
    delivery_count = Column(Integer, nullable=False, default=0)
    failure_count = Column(Integer, nullable=False, default=0)

    # Configuration
    headers = Column(JsonType(), nullable=True)
    retry_policy = Column(JsonType(), nullable=True)
    webhook_metadata = Column("metadata", JsonType(), nullable=True)

    # Tracking
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Indexes
    __table_args__ = (
        Index("idx_webhook_event_active", "event_type", "active"),
        Index("idx_webhook_updated", "updated_at"),
    )

    def __repr__(self) -> str:
        return f"<WebhookRecord(id={self.id}, event_type={self.event_type}, active={self.active})>"


class PerformanceMetric(Base, BaseModel):
    """Store performance metrics."""

    __tablename__ = "performance_metrics"

    # Primary key
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)

    # Metric info
    metric_name = Column(String(255), nullable=False, index=True)
    value = Column(Float, nullable=False)

    # Tagging
    tags = Column(JsonType(), nullable=True)
    metric_metadata = Column("metadata", JsonType(), nullable=True)

    # Timestamp
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    # Indexes
    __table_args__ = (
        Index("idx_metric_name_timestamp", "metric_name", "timestamp"),
    )

    def __repr__(self) -> str:
        return f"<PerformanceMetric(metric_name={self.metric_name}, value={self.value})>"


class ErrorLog(Base, BaseModel):
    """Log errors and exceptions."""

    __tablename__ = "error_logs"

    # Primary key
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)

    # Error info
    error_type = Column(String(255), nullable=False, index=True)
    message = Column(Text, nullable=False)
    traceback = Column(Text, nullable=True)

    # Context
    context = Column(JsonType(), nullable=True)
    severity = Column(String(50), nullable=False, index=True)  # critical, error, warning

    # Tracking
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    resolved = Column(Boolean, nullable=False, default=False)

    # Indexes
    __table_args__ = (
        Index("idx_error_type_timestamp", "error_type", "timestamp"),
        Index("idx_error_severity_resolved", "severity", "resolved"),
    )

    def __repr__(self) -> str:
        return f"<ErrorLog(id={self.id}, error_type={self.error_type}, severity={self.severity})>"
