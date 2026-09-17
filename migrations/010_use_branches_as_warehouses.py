from __future__ import annotations

from sqlalchemy import inspect, text

revision = "0010"

WAREHOUSE_FK_TABLES = ("stk_balance", "stk_ledger", "stk_config", "stk_allocation")


def _warehouse_fks(bind, table_name: str) -> list[dict]:
    return [
        fk
        for fk in inspect(bind).get_foreign_keys(table_name)
        if fk.get("constrained_columns") == ["warehouse_id"]
    ]


def upgrade(db) -> None:
    bind = db.connection()
    inspector = inspect(bind)
    existing_tables = set(inspector.get_table_names())

    for table_name in WAREHOUSE_FK_TABLES:
        if table_name not in existing_tables:
            continue

        existing = _warehouse_fks(bind, table_name)
        for fk in existing:
            if fk.get("referred_table") != "branches":
                bind.execute(text(f'ALTER TABLE {table_name} DROP CONSTRAINT "{fk["name"]}"'))

        has_branch_fk = any(fk.get("referred_table") == "branches" for fk in existing)
        if not has_branch_fk:
            bind.execute(
                text(
                    f"ALTER TABLE {table_name} "
                    f"ADD CONSTRAINT fk_{table_name}_warehouse_id_branches "
                    "FOREIGN KEY (warehouse_id) REFERENCES branches(id)"
                )
            )


def downgrade(db) -> None:
    bind = db.connection()
    inspector = inspect(bind)
    existing_tables = set(inspector.get_table_names())

    for table_name in WAREHOUSE_FK_TABLES:
        if table_name not in existing_tables:
            continue

        for fk in _warehouse_fks(bind, table_name):
            if fk.get("referred_table") == "branches":
                bind.execute(text(f'ALTER TABLE {table_name} DROP CONSTRAINT "{fk["name"]}"'))
