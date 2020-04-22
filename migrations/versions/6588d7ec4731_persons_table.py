"""persons table

Revision ID: 6588d7ec4731
Revises: 
Create Date: 2020-03-05 10:26:25.551336

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6588d7ec4731'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('person',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('color', sa.String(length=64), nullable=True),
    sa.Column('mod_time', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_person_color'), 'person', ['color'], unique=False)
    op.create_index(op.f('ix_person_mod_time'), 'person', ['mod_time'], unique=False)
    op.create_index(op.f('ix_person_username'), 'person', ['username'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_person_username'), table_name='person')
    op.drop_index(op.f('ix_person_mod_time'), table_name='person')
    op.drop_index(op.f('ix_person_color'), table_name='person')
    op.drop_table('person')
    # ### end Alembic commands ###