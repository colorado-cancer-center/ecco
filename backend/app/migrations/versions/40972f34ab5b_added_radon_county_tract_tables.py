"""Added Radon county, tract tables

Revision ID: 40972f34ab5b
Revises: 614c25756e6b
Create Date: 2024-06-20 17:27:17.528577

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '40972f34ab5b'
down_revision: Union[str, None] = '614c25756e6b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('radoncounty',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('FIPS', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('County', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('State', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('measure', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('value', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['State'], ['us_state.name'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_radoncounty_County'), 'radoncounty', ['County'], unique=False)
    op.create_index(op.f('ix_radoncounty_FIPS'), 'radoncounty', ['FIPS'], unique=False)
    op.create_index(op.f('ix_radoncounty_State'), 'radoncounty', ['State'], unique=False)
    op.create_index(op.f('ix_radoncounty_measure'), 'radoncounty', ['measure'], unique=False)
    op.create_table('radontract',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('FIPS', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('County', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('State', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('measure', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('value', sa.Float(), nullable=True),
    sa.Column('Tract', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.ForeignKeyConstraint(['State'], ['us_state.name'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_radontract_County'), 'radontract', ['County'], unique=False)
    op.create_index(op.f('ix_radontract_FIPS'), 'radontract', ['FIPS'], unique=False)
    op.create_index(op.f('ix_radontract_State'), 'radontract', ['State'], unique=False)
    op.create_index(op.f('ix_radontract_Tract'), 'radontract', ['Tract'], unique=False)
    op.create_index(op.f('ix_radontract_measure'), 'radontract', ['measure'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_radontract_measure'), table_name='radontract')
    op.drop_index(op.f('ix_radontract_Tract'), table_name='radontract')
    op.drop_index(op.f('ix_radontract_State'), table_name='radontract')
    op.drop_index(op.f('ix_radontract_FIPS'), table_name='radontract')
    op.drop_index(op.f('ix_radontract_County'), table_name='radontract')
    op.drop_table('radontract')
    op.drop_index(op.f('ix_radoncounty_measure'), table_name='radoncounty')
    op.drop_index(op.f('ix_radoncounty_State'), table_name='radoncounty')
    op.drop_index(op.f('ix_radoncounty_FIPS'), table_name='radoncounty')
    op.drop_index(op.f('ix_radoncounty_County'), table_name='radoncounty')
    op.drop_table('radoncounty')
    # ### end Alembic commands ###