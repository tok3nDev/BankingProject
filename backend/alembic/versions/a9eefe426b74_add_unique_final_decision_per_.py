"""add unique final decision per application

Revision ID: a9eefe426b74
Revises: d645a1e3dc87
Create Date: 2026-11-26 19:11:45.441304

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a9eefe426b74"
down_revision: str | Sequence[str] | None = "d645a1e3dc87"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(
        "uq_credit_decisions_one_final_per_application",
        "credit_decisions",
        ["application_id"],
        unique=True,
        postgresql_where=sa.text("decision_status IN ('approved', 'rejected')"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        "uq_credit_decisions_one_final_per_application",
        table_name="credit_decisions",
        postgresql_where=sa.text("decision_status IN ('approved', 'rejected')"),
    )
