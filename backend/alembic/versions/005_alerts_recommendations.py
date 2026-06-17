from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "005_alerts_recommendations"
down_revision = "004_profiles_segments"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("alerts", sa.Column("alert_id", sa.String(64), primary_key=True))
    op.create_table("recommendation_insights", sa.Column("insight_id", sa.String(64), primary_key=True))


def downgrade() -> None:
    op.drop_table("recommendation_insights")
    op.drop_table("alerts")
