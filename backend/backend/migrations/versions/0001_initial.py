"""Initial migration: create core tables"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as psql

# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('users',
        sa.Column('id', psql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(length=255), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(length=512), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table('user_settings',
        sa.Column('id', psql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', psql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('theme', sa.String(length=50), nullable=True),
        sa.Column('language', sa.String(length=10), nullable=True),
        sa.Column('font_size', sa.Integer(), nullable=True),
        sa.Column('response_length', sa.Integer(), nullable=True),
        sa.Column('temperature', sa.Integer(), nullable=True),
        sa.Column('max_tokens', sa.Integer(), nullable=True),
        sa.Column('streaming', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_table('auth_sessions',
        sa.Column('id', psql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', psql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('refresh_token_hash', sa.String(length=512), nullable=False),
        sa.Column('issued_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table('conversations',
        sa.Column('id', psql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', psql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_message_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table('messages',
        sa.Column('id', psql.UUID(as_uuid=True), primary_key=True),
        sa.Column('conversation_id', psql.UUID(as_uuid=True), sa.ForeignKey('conversations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('sender', sa.String(length=50), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_table('feedback',
        sa.Column('id', psql.UUID(as_uuid=True), primary_key=True),
        sa.Column('message_id', psql.UUID(as_uuid=True), sa.ForeignKey('messages.id', ondelete='SET NULL'), nullable=True),
        sa.Column('user_id', psql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('thumbs_up', sa.Boolean(), nullable=True),
        sa.Column('thumbs_down', sa.Boolean(), nullable=True),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_table('uploads',
        sa.Column('id', psql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', psql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('filename', sa.String(length=1024), nullable=False),
        sa.Column('path', sa.String(length=2048), nullable=False),
        sa.Column('mime', sa.String(length=255), nullable=True),
        sa.Column('size', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )


def downgrade():
    op.drop_table('uploads')
    op.drop_table('feedback')
    op.drop_table('messages')
    op.drop_table('conversations')
    op.drop_table('auth_sessions')
    op.drop_table('user_settings')
    op.drop_table('users')
