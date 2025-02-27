"""Turn user unique by email

Revision ID: 5fc86b2c9dde
Revises: bc81aa7eabb3
Create Date: 2025-01-12 19:41:19.189558

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "5fc86b2c9dde"
down_revision: Union[str, None] = "bc81aa7eabb3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint("user_email_unique", "user", ["email"])


def downgrade() -> None:
    op.drop_constraint("user_email_unique", "user")
