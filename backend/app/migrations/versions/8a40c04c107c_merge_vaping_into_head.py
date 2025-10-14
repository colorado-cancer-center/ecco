"""merge vaping into head

Revision ID: 8a40c04c107c
Revises: 4c47c1001dc4, 7214c6efee37
Create Date: 2025-09-30 10:22:40.854491

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '8a40c04c107c'
down_revision: Union[str, None] = ('4c47c1001dc4', '7214c6efee37')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
