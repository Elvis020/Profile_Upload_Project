"""initialized table

Revision ID: c4ea4cddd1eb
Revises: 
Create Date: 2023-01-30 14:40:32.242533

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c4ea4cddd1eb'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('email', sa.String(50), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('users')
