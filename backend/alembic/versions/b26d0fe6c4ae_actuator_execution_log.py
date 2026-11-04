"""actuator_execution_log

Revision ID: b26d0fe6c4ae
Revises: 7d2a1db5b0c8
Create Date: 2026-11-04 11:59:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'b26d0fe6c4ae'
down_revision: Union[str, Sequence[str], None] = '7d2a1db5b0c8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'actuator_execution_log',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('device_id', sa.UUID(), nullable=False),
        sa.Column('success', sa.Boolean(), nullable=False),
        sa.Column('policy_applied', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column(
            'created_at',
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(['device_id'], ['devices.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_actuator_execution_log_device_id', 'actuator_execution_log', ['device_id'], unique=False)
    op.create_index('ix_actuator_execution_log_created_at', 'actuator_execution_log', ['created_at'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_actuator_execution_log_created_at', table_name='actuator_execution_log')
    op.drop_index('ix_actuator_execution_log_device_id', table_name='actuator_execution_log')
    op.drop_table('actuator_execution_log')
