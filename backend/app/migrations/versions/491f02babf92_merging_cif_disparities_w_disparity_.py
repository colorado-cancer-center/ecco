"""Merging CIF disparities w/disparity index

Revision ID: 491f02babf92
Revises: 63a524442a63, ac38d640299a
Create Date: 2024-03-18 19:33:49.327308

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '491f02babf92'
down_revision: Union[str, None] = ('63a524442a63', 'ac38d640299a')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
