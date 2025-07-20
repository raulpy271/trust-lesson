"""add title column on lesson

Revision ID: 8e836ae377c4
Revises: d13f31069b13
Create Date: 2025-07-20 15:11:17.837314

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8e836ae377c4"
down_revision: Union[str, None] = "d13f31069b13"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("lesson", sa.Column("title", sa.String(length=100), nullable=False))


def downgrade() -> None:
    op.drop_column("lesson", "title")
