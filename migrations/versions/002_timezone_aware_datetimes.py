"""Convert to timezone-aware datetimes

Revision ID: 002
Revises: 001
Create Date: 2025-01-27 12:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # No schema changes needed - this is a code-level fix
    # All datetime columns remain the same but now use UTC-aware defaults
    pass


def downgrade():
    # No schema changes to revert
    pass