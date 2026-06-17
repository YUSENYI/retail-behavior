from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "002_behavior_events"
down_revision = "001_foundation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "behavior_events",
        sa.Column("event_pk", sa.Integer, primary_key=True),
        sa.Column("event_id", sa.String(128), nullable=False),
        sa.Column("source_system", sa.String(64), nullable=False),
        sa.Column("event_type", sa.String(32), nullable=False),
        sa.Column("session_id", sa.String(64), nullable=False),
        sa.Column("channel_id", sa.String(64), nullable=False),
        sa.Column("occurred_at", sa.DateTime, nullable=False),
        sa.Column("received_at", sa.DateTime, nullable=False),
        sa.Column("idempotency_state", sa.String(32), nullable=False),
        sa.UniqueConstraint("source_system", "event_id", name="uq_behavior_event_source_event"),
    )


def downgrade() -> None:
    op.drop_table("behavior_events")
