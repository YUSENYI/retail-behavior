from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "003_metrics"
down_revision = "002_behavior_events"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("metric_definitions", sa.Column("metric_key", sa.String(64), primary_key=True), sa.Column("version", sa.String(32), primary_key=True))
    op.create_table("metric_snapshots", sa.Column("snapshot_id", sa.String(64), primary_key=True))
    op.create_table("funnel_stage_snapshots", sa.Column("snapshot_id", sa.String(64), primary_key=True))


def downgrade() -> None:
    op.drop_table("funnel_stage_snapshots")
    op.drop_table("metric_snapshots")
    op.drop_table("metric_definitions")
