"""change primary key in user identity table

Revision ID: 04f628b988a7
Revises: d6294ab12aba
Create Date: 2025-09-21 12:14:22.608896

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "04f628b988a7"
down_revision: Union[str, None] = "d6294ab12aba"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("user_identity", sa.Column("id", sa.Uuid(), nullable=False))
    op.drop_constraint("user_identity_pkey", "user_identity", type_="primary")
    op.create_primary_key("user_identity_pkey", "user_identity", ["id"])
    op.create_unique_constraint(None, "user_identity", ["user_id"])


def downgrade() -> None:
    op.drop_constraint("user_identity_user_id_key", "user_identity", type_="unique")
    op.drop_constraint("user_identity_pkey", "user_identity", type_="primary")
    op.create_primary_key("user_identity_pkey", "user_identity", ["user_id"])
    op.drop_column("user_identity", "id")
