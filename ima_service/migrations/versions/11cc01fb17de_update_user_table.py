"""update user table safely (idempotent)

Revision ID: 11cc01fb17de
Revises: ebbc85396987
Create Date: 2025-10-16 16:20:18.454561

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "11cc01fb17de"
down_revision: Union[str, Sequence[str], None] = "ebbc85396987"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema safely and idempotently."""

    # Drop index and column if they exist
    with op.batch_alter_table("auth_tokens") as batch_op:
        batch_op.drop_index("idx_auth_token_revoked_user", if_exists=True)
    with op.batch_alter_table("invitation_tokens") as batch_op:
        batch_op.drop_column("expires_at", if_exists=True)

    # Add 'is_super_user' column if it doesn't exist
    conn = op.get_bind()
    insp = sa.inspect(conn)
    if "is_super_user" not in [c["name"] for c in insp.get_columns("users")]:
        op.add_column("users", sa.Column("is_super_user", sa.Boolean(), nullable=True))
        # Backfill existing rows
        op.execute("UPDATE users SET is_super_user = FALSE WHERE is_super_user IS NULL")
        # Make NOT NULL
        op.alter_column("users", "is_super_user", nullable=False)


def downgrade() -> None:
    """Downgrade schema safely."""

    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("is_super_user", if_exists=True)

    with op.batch_alter_table("invitation_tokens") as batch_op:
        batch_op.add_column(
            sa.Column(
                "expires_at",
                postgresql.TIMESTAMP(timezone=True),
                autoincrement=False,
                nullable=True,
            )
        )

    with op.batch_alter_table("auth_tokens") as batch_op:
        batch_op.create_index("idx_auth_token_revoked_user", ["revoked", "user_id"], unique=False)
