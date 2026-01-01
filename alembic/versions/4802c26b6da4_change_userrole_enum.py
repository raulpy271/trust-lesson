"""Change userrole ENUM

Revision ID: 4802c26b6da4
Revises: 3a4c4c1e8bfe
Create Date: 2025-12-26 13:42:45.502532

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "4802c26b6da4"
down_revision: Union[str, None] = "3a4c4c1e8bfe"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE userrole RENAME VALUE 'STUDANT' TO 'STUDENT'")


def downgrade() -> None:
    op.execute("ALTER TYPE userrole RENAME VALUE 'STUDENT' TO 'STUDANT'")
