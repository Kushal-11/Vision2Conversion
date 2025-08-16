"""Add missing user columns

Revision ID: add_missing_user_columns
Revises: cc24a9b3fd4e
Create Date: 2025-08-16 23:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_missing_user_columns'
down_revision: str = 'cc24a9b3fd4e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add missing columns to users table
    op.add_column('users', sa.Column('hashed_password', sa.String(), nullable=True))
    op.add_column('users', sa.Column('full_name', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('users', sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    # Remove the added columns
    op.drop_column('users', 'is_superuser')
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'full_name')
    op.drop_column('users', 'hashed_password') 