"""rename image name to object_key

Revision ID: afa245ae840a
Revises: b5c2399bfc67
Create Date: 2026-06-09 11:38:12.394637
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "afa245ae840a"
down_revision: Union[str, Sequence[str], None] = "b5c2399bfc67"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "listing_images",
        "name",
        new_column_name="object_key",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "listing_images",
        "object_key",
        new_column_name="name",
    )
