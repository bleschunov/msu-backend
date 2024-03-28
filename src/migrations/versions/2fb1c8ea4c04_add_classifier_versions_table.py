"""add classifier versions table

Revision ID: 2fb1c8ea4c04
Revises: 07488a574e53
Create Date: 2024-03-28 04:44:10.939216

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '2fb1c8ea4c04'
down_revision: Union[str, None] = '07488a574e53'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('classifier_version',
    sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('accuracy', sa.Float(), nullable=True),
    sa.Column('is_deleted', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('nomenclature')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('nomenclature',
    sa.Column('id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('nomenclature', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('group', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('embeddings', sa.VARCHAR(), autoincrement=False, nullable=True)
    )
    op.drop_table('classifier_version')
    # ### end Alembic commands ###
