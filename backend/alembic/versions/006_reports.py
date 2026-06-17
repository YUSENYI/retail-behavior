from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "006_reports"
down_revision = "005_alerts_recommendations"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("reports", sa.Column("report_id", sa.String(64), primary_key=True))


def downgrade() -> None:
    op.drop_table("reports")
