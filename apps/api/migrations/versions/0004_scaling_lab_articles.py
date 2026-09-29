"""Add scaling-lab article fields and notifications."""

import sqlalchemy as sa
from alembic import op

revision = "0004_scaling_lab_articles"
down_revision = "0003_posts"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "posts",
        sa.Column("title", sa.String(200), nullable=False, server_default="Untitled"),
    )
    op.add_column(
        "posts",
        sa.Column("view_count", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("reference_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])
    op.create_index("ix_notifications_reference_id", "notifications", ["reference_id"])


def downgrade() -> None:
    op.drop_index("ix_notifications_reference_id", table_name="notifications")
    op.drop_index("ix_notifications_user_id", table_name="notifications")
    op.drop_table("notifications")
    op.drop_column("posts", "view_count")
    op.drop_column("posts", "title")
