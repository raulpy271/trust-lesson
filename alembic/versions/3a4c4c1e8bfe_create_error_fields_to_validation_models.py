"""Create error fields to validation models

Revision ID: 3a4c4c1e8bfe
Revises: 39faa71875fa
Create Date: 2025-10-14 21:22:10.207980

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3a4c4c1e8bfe"
down_revision: Union[str, None] = "39faa71875fa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "identity_validation",
        sa.Column("error_message", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "identity_validation", sa.Column("error_traceback", sa.Text(), nullable=True)
    )
    op.add_column(
        "lesson_validation",
        sa.Column("error_message", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "lesson_validation", sa.Column("error_traceback", sa.Text(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("lesson_validation", "error_traceback")
    op.drop_column("lesson_validation", "error_message")
    op.drop_column("identity_validation", "error_traceback")
    op.drop_column("identity_validation", "error_message")
