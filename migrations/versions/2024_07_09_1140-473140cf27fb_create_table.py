"""Create table

Revision ID: 473140cf27fb
Revises: 
Create Date: 2024-07-09 11:40:28.578819

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '473140cf27fb'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('order_types',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id', 'name')
    )
    op.create_index(op.f('ix_order_types_name'), 'order_types', ['name'], unique=True)
    op.create_table('user_sessions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('session_id', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_sessions_session_id'), 'user_sessions', ['session_id'], unique=True)
    op.create_table('orders',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('weight', sa.Numeric(precision=10, scale=3), nullable=True),
    sa.Column('cost', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('delivery_cost', sa.String(), nullable=True),
    sa.Column('session_uuid', sa.String(), nullable=True),
    sa.Column('order_type_name', sa.String(), nullable=True),
    sa.Column('background_task_id', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['order_type_name'], ['order_types.name'], ),
    sa.ForeignKeyConstraint(['session_uuid'], ['user_sessions.session_id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('background_task_id')
    )
    op.create_index(op.f('ix_orders_id'), 'orders', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_orders_id'), table_name='orders')
    op.drop_table('orders')
    op.drop_index(op.f('ix_user_sessions_session_id'), table_name='user_sessions')
    op.drop_table('user_sessions')
    op.drop_index(op.f('ix_order_types_name'), table_name='order_types')
    op.drop_table('order_types')
    # ### end Alembic commands ###
