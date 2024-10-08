"""added disparity index table

Revision ID: ac38d640299a
Revises: 56c1a3bb17d7
Create Date: 2024-03-15 22:16:22.920436

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'ac38d640299a'
down_revision: Union[str, None] = '56c1a3bb17d7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('cancerdisparitiesindex',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('FIPS', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('County', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('State', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('measure', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('value', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['State'], ['us_state.name'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cancerdisparitiesindex_County'), 'cancerdisparitiesindex', ['County'], unique=False)
    op.create_index(op.f('ix_cancerdisparitiesindex_FIPS'), 'cancerdisparitiesindex', ['FIPS'], unique=False)
    op.create_index(op.f('ix_cancerdisparitiesindex_State'), 'cancerdisparitiesindex', ['State'], unique=False)
    op.create_index(op.f('ix_cancerdisparitiesindex_measure'), 'cancerdisparitiesindex', ['measure'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_cancerdisparitiesindex_measure'), table_name='cancerdisparitiesindex')
    op.drop_index(op.f('ix_cancerdisparitiesindex_State'), table_name='cancerdisparitiesindex')
    op.drop_index(op.f('ix_cancerdisparitiesindex_FIPS'), table_name='cancerdisparitiesindex')
    op.drop_index(op.f('ix_cancerdisparitiesindex_County'), table_name='cancerdisparitiesindex')
    op.drop_table('cancerdisparitiesindex')
    # ### end Alembic commands ###
