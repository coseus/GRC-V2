"""initial

Revision ID: 0001_initial
Revises:
Create Date: 2026-03-22
"""
from alembic import op
import sqlalchemy as sa

revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('username', sa.String(length=255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_table('companies',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False, unique=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_table('assessments',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('company_id', sa.Integer(), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('framework_code', sa.String(length=100), nullable=False),
        sa.Column('framework_name', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_table('answers',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('assessment_id', sa.Integer(), sa.ForeignKey('assessments.id', ondelete='CASCADE'), nullable=False),
        sa.Column('domain_id', sa.String(length=100)),
        sa.Column('domain_name', sa.String(length=255)),
        sa.Column('question_id', sa.String(length=100), nullable=False),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('answer_value', sa.Text()),
        sa.Column('score', sa.Integer()),
        sa.Column('notes', sa.Text()),
        sa.Column('proof', sa.Text()),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('assessment_id', 'question_id', name='uq_answer_assessment_question')
    )
    op.create_table('executive_summary',
        sa.Column('assessment_id', sa.Integer(), sa.ForeignKey('assessments.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('summary', sa.Text()),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_table('recommendations',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('assessment_id', sa.Integer(), sa.ForeignKey('assessments.id', ondelete='CASCADE'), nullable=False),
        sa.Column('domain_id', sa.String(length=100)),
        sa.Column('domain_name', sa.String(length=255)),
        sa.Column('source', sa.String(length=50), nullable=False),
        sa.Column('recommendation_key', sa.String(length=255)),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('risk', sa.String(length=50), nullable=False),
        sa.Column('responsible', sa.String(length=255)),
        sa.Column('deadline', sa.Date()),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_table('audit_logs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('actor_user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('entity_type', sa.String(length=100), nullable=False),
        sa.Column('entity_id', sa.String(length=100)),
        sa.Column('details_json', sa.Text()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )

def downgrade():
    op.drop_table('audit_logs')
    op.drop_table('recommendations')
    op.drop_table('executive_summary')
    op.drop_table('answers')
    op.drop_table('assessments')
    op.drop_table('companies')
    op.drop_table('users')
