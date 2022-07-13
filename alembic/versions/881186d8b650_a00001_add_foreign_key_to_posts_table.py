"""A00001 add foreign key to posts table

Revision ID: 881186d8b650
Revises: 299110c81317
Create Date: 2022-07-13 15:03:26.917123

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '881186d8b650'
down_revision = '299110c81317'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('user_id', sa.Integer(), nullable=False))
    op.create_foreign_key('posts_users_fk', source_table="posts", referent_table="users", local_cols=['user_id'], remote_cols=['id'], ondelete="CASCADE")
    pass


def downgrade() -> None:
    op.drop_constraint('posts_users_fk', table_name="posts")
    op.drop_column('posts', 'user_id')
    pass
