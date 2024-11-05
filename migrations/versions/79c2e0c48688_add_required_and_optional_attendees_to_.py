"""Add required and optional attendees to Event model

Revision ID: 79c2e0c48688
Revises: d8a38670be01
Create Date: 2024-10-31 00:17:28.583288

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '79c2e0c48688'
down_revision = 'd8a38670be01'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('event', schema=None) as batch_op:
        batch_op.add_column(sa.Column('required_attendees', sa.PickleType(), nullable=True))
        batch_op.add_column(sa.Column('optional_attendees', sa.PickleType(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('event', schema=None) as batch_op:
        batch_op.drop_column('optional_attendees')
        batch_op.drop_column('required_attendees')

    # ### end Alembic commands ###
