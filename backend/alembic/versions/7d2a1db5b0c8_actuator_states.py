"""actuator_states

Revision ID: 7d2a1db5b0c8
Revises: 0a4c3f5c8b6f
Create Date: 2026-10-30 17:17:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '7d2a1db5b0c8'
down_revision: Union[str, Sequence[str], None] = '0a4c3f5c8b6f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'actuator_states',
        sa.Column('device_id', sa.UUID(), nullable=False),
        sa.Column('state', sa.String(length=32), server_default='idle', nullable=False),
        sa.Column(
            'updated_at',
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(['device_id'], ['devices.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('device_id'),
    )
    op.execute(
        """
        INSERT INTO actuator_states (device_id, state, updated_at)
        SELECT d.id, 'idle', now()
        FROM devices AS d
        WHERE d.role = 'actuator'
        ON CONFLICT (device_id) DO NOTHING
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('actuator_states')
