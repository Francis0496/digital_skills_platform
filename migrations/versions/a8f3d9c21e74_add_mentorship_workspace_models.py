"""add mentorship workspace models

Revision ID: a8f3d9c21e74
Revises: c0c6916a5bfe
Create Date: 2026-08-24 07:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "a8f3d9c21e74"
down_revision = "c0c6916a5bfe"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "mentorship_goal",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("mentorship_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["mentorship_id"], ["mentorship.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_mentorship_goal_mentorship_id"),
        "mentorship_goal",
        ["mentorship_id"],
        unique=False,
    )
    op.create_table(
        "mentorship_progress_update",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("mentorship_id", sa.Integer(), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.Column("goal_id", sa.Integer(), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["author_id"], ["user.id"]),
        sa.ForeignKeyConstraint(["goal_id"], ["mentorship_goal.id"]),
        sa.ForeignKeyConstraint(["mentorship_id"], ["mentorship.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_mentorship_progress_update_mentorship_id"),
        "mentorship_progress_update",
        ["mentorship_id"],
        unique=False,
    )
    op.create_table(
        "mentorship_feedback",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("mentorship_id", sa.Integer(), nullable=False),
        sa.Column("mentor_id", sa.Integer(), nullable=False),
        sa.Column("progress_update_id", sa.Integer(), nullable=True),
        sa.Column("goal_id", sa.Integer(), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["goal_id"], ["mentorship_goal.id"]),
        sa.ForeignKeyConstraint(["mentor_id"], ["user.id"]),
        sa.ForeignKeyConstraint(
            ["progress_update_id"], ["mentorship_progress_update.id"]
        ),
        sa.ForeignKeyConstraint(["mentorship_id"], ["mentorship.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_mentorship_feedback_mentorship_id"),
        "mentorship_feedback",
        ["mentorship_id"],
        unique=False,
    )


def downgrade():
    op.drop_index(
        op.f("ix_mentorship_feedback_mentorship_id"),
        table_name="mentorship_feedback",
    )
    op.drop_table("mentorship_feedback")
    op.drop_index(
        op.f("ix_mentorship_progress_update_mentorship_id"),
        table_name="mentorship_progress_update",
    )
    op.drop_table("mentorship_progress_update")
    op.drop_index(
        op.f("ix_mentorship_goal_mentorship_id"), table_name="mentorship_goal"
    )
    op.drop_table("mentorship_goal")
