from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "001_foundation"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("users", sa.Column("user_id", sa.String(64), primary_key=True))
    op.create_table("visitors", sa.Column("visitor_id", sa.String(64), primary_key=True))
    op.create_table("channels", sa.Column("channel_id", sa.String(64), primary_key=True))
    op.create_table("sessions", sa.Column("session_id", sa.String(64), primary_key=True))
    op.create_table("products", sa.Column("product_id", sa.String(64), primary_key=True))
    op.create_table("orders", sa.Column("order_id", sa.String(64), primary_key=True))
    op.create_table("payments", sa.Column("payment_id", sa.String(64), primary_key=True))
    op.create_table("role_permissions", sa.Column("permission_id", sa.Integer, primary_key=True))
    op.create_table("audit_logs", sa.Column("audit_id", sa.String(64), primary_key=True))


def downgrade() -> None:
    for table in [
        "audit_logs",
        "role_permissions",
        "payments",
        "orders",
        "products",
        "sessions",
        "channels",
        "visitors",
        "users",
    ]:
        op.drop_table(table)
