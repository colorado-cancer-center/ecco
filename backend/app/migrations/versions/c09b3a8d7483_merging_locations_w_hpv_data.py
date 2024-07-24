"""Merging locations w/HPV data

Revision ID: c09b3a8d7483
Revises: cb9412070fed, bf61b2255ed0
Create Date: 2024-07-23 21:47:07.218701

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'c09b3a8d7483'
down_revision: Union[str, None] = ('cb9412070fed', 'bf61b2255ed0')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
