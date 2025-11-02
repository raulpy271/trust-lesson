"""Add user identity table

Revision ID: 7854bebd271c
Revises: 8e836ae377c4
Create Date: 2025-09-14 13:21:12.275597

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7854bebd271c"
down_revision: Union[str, None] = "8e836ae377c4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


identity_type = sa.Enum(
    "IDENTITY_CARD", "DRIVER_LICENSE", "PASSPORT", "OTHER", name="identitytype"
)


def upgrade() -> None:
    op.create_table(
        "user_identity",
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("identity_code", sa.String(), nullable=False),
        sa.Column("type", identity_type, nullable=False),
        sa.Column("fullname", sa.String(), nullable=False),
        sa.Column("parent_fullname", sa.String(), nullable=True),
        sa.Column("birth_date", sa.Date(), nullable=False),
        sa.Column("expiration_date", sa.Date(), nullable=False),
        sa.Column("issued_date", sa.Date(), nullable=True),
        sa.Column("issuing_authority", sa.String(), nullable=True),
        sa.Column("country_state", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("user_id"),
        sa.UniqueConstraint("identity_code"),
    )


def downgrade() -> None:
    op.drop_table("user_identity")
    identity_type.drop(op.get_bind())
