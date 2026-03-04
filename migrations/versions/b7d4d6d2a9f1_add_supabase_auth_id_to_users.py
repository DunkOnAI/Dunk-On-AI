"""Add supabase_auth_id to users

Revision ID: b7d4d6d2a9f1
Revises: 8db455685402
Create Date: 2026-02-19 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b7d4d6d2a9f1"
down_revision = "8db455685402"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(sa.Column("supabase_auth_id", sa.String(length=36), nullable=True))
        batch_op.create_index(batch_op.f("ix_users_supabase_auth_id"), ["supabase_auth_id"], unique=True)


def downgrade():
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_users_supabase_auth_id"))
        batch_op.drop_column("supabase_auth_id")
