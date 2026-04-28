"""person type: employee replaces resident

Revision ID: 002
Revises: 001
Create Date: 2026-04-07

"""
from typing import Sequence, Union

from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # `ALTER TYPE ... ADD VALUE` no puede usarse y luego referenciar el nuevo valor
    # dentro de la misma transacción en PostgreSQL.
    # Usamos un bloque autocommit y además lo hacemos idempotente.
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE persontype ADD VALUE IF NOT EXISTS 'employee'")
    op.execute(
        "UPDATE people SET person_type = 'employee'::persontype "
        "WHERE person_type::text = 'resident'"
    )


def downgrade() -> None:
    # PostgreSQL no permite quitar valores de un ENUM de forma trivial.
    pass
