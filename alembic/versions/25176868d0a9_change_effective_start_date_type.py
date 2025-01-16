"""Change effective_start_date type

Revision ID: 25176868d0a9
Revises: 0b15f9e0a018
Create Date: 2025-01-15 20:51:11.111111

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '25176868d0a9'
down_revision: Union[str, None] = '0b15f9e0a018'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('lesson', 'effective_start_date',
               existing_type=sa.DATE(),
               type_=sa.DateTime(),
               existing_nullable=True)
    op.alter_column('lesson', 'start_date',
               existing_type=sa.DATE(),
               type_=sa.DateTime(),
               existing_nullable=False)


def downgrade() -> None:
    op.alter_column('lesson', 'start_date',
               existing_type=sa.DateTime(),
               type_=sa.DATE(),
               existing_nullable=False)
    op.alter_column('lesson', 'effective_start_date',
               existing_type=sa.DateTime(),
               type_=sa.DATE(),
               existing_nullable=True)

