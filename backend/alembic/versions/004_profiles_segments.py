from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "004_profiles_segments"
down_revision = "003_metrics"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("user_profiles", sa.Column("profile_id", sa.String(64), primary_key=True))
    op.create_table("user_segments", sa.Column("segment_id", sa.String(64), primary_key=True))
    op.create_table("user_segment_memberships", sa.Column("membership_id", sa.Integer, primary_key=True))
    op.create_table("purchase_intents", sa.Column("intent_id", sa.String(64), primary_key=True))


def downgrade() -> None:
    op.drop_table("purchase_intents")
    op.drop_table("user_segment_memberships")
    op.drop_table("user_segments")
    op.drop_table("user_profiles")
