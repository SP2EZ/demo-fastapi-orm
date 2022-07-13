"""A00002 add user table

Revision ID: 299110c81317
Revises: 82d0a9462956
Create Date: 2022-07-13 14:24:34.343279

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '299110c81317'
down_revision = '82d0a9462956'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('password', sa.String(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    pass


def downgrade() -> None:
    op.drop_table('users')
    pass
