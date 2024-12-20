"""Initial migration with email and token columns

Revision ID: 24f50d0eb477
Revises: 
Create Date: 2024-10-30 18:49:34.657099

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '24f50d0eb477'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('_alembic_tmp_user')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('_alembic_tmp_user',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('username', sa.VARCHAR(length=150), nullable=False),
    sa.Column('password_hash', sa.VARCHAR(length=150), nullable=False),
    sa.Column('email', sa.VARCHAR(length=120), nullable=False),
    sa.Column('token', sa.VARCHAR(length=200), nullable=True),
    sa.Column('is_verified', sa.BOOLEAN(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email', name='uq_user_email'),
    sa.UniqueConstraint('username')
    )
    # ### end Alembic commands ###
