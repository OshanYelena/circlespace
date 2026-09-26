"""Create friend requests and friendships."""

import sqlalchemy as sa
from alembic import op

revision = "0002_friendships"
down_revision = "0001_identity"
branch_labels = None
depends_on = None


def upgrade() -> None:
    request_status = sa.Enum("PENDING", "ACCEPTED", "REJECTED", name="friendrequeststatus")
    op.create_table(
        "friend_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("requester_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE")),
        sa.Column("recipient_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE")),
        sa.Column("status", request_status, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("responded_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("requester_id != recipient_id", name="ck_friend_request_not_self"),
    )
    op.create_table(
        "friendships",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_low_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE")),
        sa.Column("user_high_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint("user_low_id < user_high_id", name="ck_friendship_canonical_order"),
        sa.UniqueConstraint("user_low_id", "user_high_id", name="uq_friendship_pair"),
    )


def downgrade() -> None:
    op.drop_table("friendships")
    op.drop_table("friend_requests")
