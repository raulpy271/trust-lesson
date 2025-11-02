"""Rename validated_value column on lesson validation table

Revision ID: 39faa71875fa
Revises: 04f628b988a7
Create Date: 2025-10-04 14:39:53.834213

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "39faa71875fa"
down_revision: Union[str, None] = "04f628b988a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "lesson_validation", "validated_value", new_column_name="confidence"
    )


def downgrade() -> None:
    op.alter_column(
        "lesson_validation", "confidence", new_column_name="validated_value"
    )
