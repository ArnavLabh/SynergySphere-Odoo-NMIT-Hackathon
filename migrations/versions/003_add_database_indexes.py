"""Add database indexes for performance

Revision ID: 003
Revises: 002
Create Date: 2025-01-27 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    # Single column indexes
    op.create_index('ix_project_name', 'project', ['name'])
    op.create_index('ix_project_owner_id', 'project', ['owner_id'])
    op.create_index('ix_project_created_at', 'project', ['created_at'])
    op.create_index('ix_project_member_project_id', 'project_member', ['project_id'])
    op.create_index('ix_project_member_user_id', 'project_member', ['user_id'])
    op.create_index('ix_project_member_role', 'project_member', ['role'])
    op.create_index('ix_task_project_id', 'task', ['project_id'])
    op.create_index('ix_task_title', 'task', ['title'])
    op.create_index('ix_task_assignee_id', 'task', ['assignee_id'])
    op.create_index('ix_task_due_date', 'task', ['due_date'])
    op.create_index('ix_task_status', 'task', ['status'])
    op.create_index('ix_task_priority', 'task', ['priority'])
    op.create_index('ix_task_created_at', 'task', ['created_at'])
    op.create_index('ix_task_updated_at', 'task', ['updated_at'])
    op.create_index('ix_message_project_id', 'message', ['project_id'])
    op.create_index('ix_message_user_id', 'message', ['user_id'])
    op.create_index('ix_message_parent_id', 'message', ['parent_id'])
    op.create_index('ix_message_created_at', 'message', ['created_at'])
    
    # Composite indexes for common query patterns
    op.create_index('ix_project_member_composite', 'project_member', ['project_id', 'user_id'])
    op.create_index('ix_task_project_status', 'task', ['project_id', 'status'])
    op.create_index('ix_task_assignee_status', 'task', ['assignee_id', 'status'])
    op.create_index('ix_message_project_created', 'message', ['project_id', 'created_at'])
    op.create_index('ix_message_thread', 'message', ['parent_id', 'created_at'])


def downgrade():
    # Remove composite indexes
    op.drop_index('ix_message_thread', 'message')
    op.drop_index('ix_message_project_created', 'message')
    op.drop_index('ix_task_assignee_status', 'task')
    op.drop_index('ix_task_project_status', 'task')
    op.drop_index('ix_project_member_composite', 'project_member')
    
    # Remove single column indexes
    op.drop_index('ix_message_created_at', 'message')
    op.drop_index('ix_message_parent_id', 'message')
    op.drop_index('ix_message_user_id', 'message')
    op.drop_index('ix_message_project_id', 'message')
    op.drop_index('ix_task_updated_at', 'task')
    op.drop_index('ix_task_created_at', 'task')
    op.drop_index('ix_task_priority', 'task')
    op.drop_index('ix_task_status', 'task')
    op.drop_index('ix_task_due_date', 'task')
    op.drop_index('ix_task_assignee_id', 'task')
    op.drop_index('ix_task_title', 'task')
    op.drop_index('ix_task_project_id', 'task')
    op.drop_index('ix_project_member_role', 'project_member')
    op.drop_index('ix_project_member_user_id', 'project_member')
    op.drop_index('ix_project_member_project_id', 'project_member')
    op.drop_index('ix_project_created_at', 'project')
    op.drop_index('ix_project_owner_id', 'project')
    op.drop_index('ix_project_name', 'project')