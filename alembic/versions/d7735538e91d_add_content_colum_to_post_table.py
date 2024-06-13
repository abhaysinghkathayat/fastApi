"""add content colum to post table

Revision ID: d7735538e91d
Revises: e39f9cd60220
Create Date: 2024-06-14 01:03:06.770476

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd7735538e91d'
down_revision: Union[str, None] = 'e39f9cd60220'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('posts',sa.Column('content',sa.String(),nullable=False))
    pass


def downgrade() -> None:
    op.drop_column("posts","content")
    pass
