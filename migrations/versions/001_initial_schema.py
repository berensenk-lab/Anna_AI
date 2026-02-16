"""Initial schema - Phase 3 tables

Revision ID: 001
Revises:
Create Date: 2025-01-18

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # memory_entries
    op.create_table(
        "memory_entries",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("tier", sa.Enum("short", "medium", "long", "base", name="memorytier"), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("embedding", sa.LargeBinary(), nullable=True),
        sa.Column("embedding_model", sa.String(100), nullable=True),
        sa.Column("tags", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("related_ids", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("accessed_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_memory_tier_timestamp", "memory_entries", ["tier", "timestamp"], unique=False)
    op.create_index("idx_memory_tags", "memory_entries", ["tags"], unique=False, postgresql_using="gin")
    op.create_index("idx_memory_expires", "memory_entries", ["expires_at"], unique=False)

    # config_entries
    op.create_table(
        "config_entries",
        sa.Column("id", sa.String(255), nullable=False),
        sa.Column("value", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("type_hint", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("changed_by", sa.String(255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_config_updated", "config_entries", ["updated_at"], unique=False)

    # sessions
    op.create_table(
        "sessions",
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.String(255), nullable=True),
        sa.Column("api_key_hash", sa.String(255), nullable=True),
        sa.Column("data", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("last_activity", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("session_id"),
    )
    op.create_index("idx_session_expires", "sessions", ["expires_at"], unique=False)
    op.create_index("idx_session_active", "sessions", ["is_active"], unique=False)
    op.create_index("idx_session_user", "sessions", ["user_id"], unique=False)

    # audit_logs
    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.String(255), nullable=True),
        sa.Column("api_key_hash", sa.String(255), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("resource_type", sa.String(100), nullable=False),
        sa.Column("resource_id", sa.String(255), nullable=True),
        sa.Column("details", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("changes", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("ip_address", sa.String(50), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_audit_user_timestamp", "audit_logs", ["user_id", "timestamp"], unique=False)
    op.create_index("idx_audit_action_timestamp", "audit_logs", ["action", "timestamp"], unique=False)
    op.create_index("idx_audit_resource", "audit_logs", ["resource_type", "resource_id"], unique=False)

    # webhooks
    op.create_table(
        "webhooks",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("url", sa.String(2048), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("last_delivery_at", sa.DateTime(), nullable=True),
        sa.Column("last_delivery_status", sa.Integer(), nullable=True),
        sa.Column("delivery_count", sa.Integer(), nullable=False),
        sa.Column("failure_count", sa.Integer(), nullable=False),
        sa.Column("headers", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("retry_policy", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_webhook_event_active", "webhooks", ["event_type", "active"], unique=False)
    op.create_index("idx_webhook_updated", "webhooks", ["updated_at"], unique=False)

    # performance_metrics
    op.create_table(
        "performance_metrics",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("metric_name", sa.String(255), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("tags", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_metric_name_timestamp", "performance_metrics", ["metric_name", "timestamp"], unique=False)

    # error_logs
    op.create_table(
        "error_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("error_type", sa.String(255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("traceback", sa.Text(), nullable=True),
        sa.Column("context", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("severity", sa.String(50), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("resolved", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_error_type_timestamp", "error_logs", ["error_type", "timestamp"], unique=False)
    op.create_index("idx_error_severity_resolved", "error_logs", ["severity", "resolved"], unique=False)


def downgrade() -> None:
    op.drop_table("error_logs")
    op.drop_table("performance_metrics")
    op.drop_table("webhooks")
    op.drop_table("audit_logs")
    op.drop_table("sessions")
    op.drop_table("config_entries")
    op.drop_table("memory_entries")
    op.execute("DROP TYPE IF EXISTS memorytier")
