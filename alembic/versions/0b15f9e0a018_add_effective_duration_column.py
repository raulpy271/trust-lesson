"""Add effective duration column

Revision ID: 0b15f9e0a018
Revises: 5fc86b2c9dde
Create Date: 2025-01-13 21:58:57.156182

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0b15f9e0a018'
down_revision: Union[str, None] = '5fc86b2c9dde'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('lesson', sa.Column('effective_duration_min', sa.Integer(), nullable=True))
    op.alter_column('lesson', 'effective_start_date',
               existing_type=sa.DATE(),
               nullable=True)


def downgrade() -> None:
    op.alter_column('lesson', 'effective_start_date',
               existing_type=sa.DATE(),
               nullable=False)
    op.drop_column('lesson', 'effective_duration_min')
