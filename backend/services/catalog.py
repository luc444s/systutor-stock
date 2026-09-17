from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session
from systutor.kernel.tenants.models import Branch

from plugins.productos.backend.models import Product


def get_product(db: Session, *, tenant_id: str, product_id: str) -> Product | None:
    return db.scalar(
        select(Product).where(
            Product.id == product_id,
            Product.tenant_id == tenant_id,
        )
    )


def require_product(db: Session, *, tenant_id: str, product_id: str) -> Product:
    product = get_product(db, tenant_id=tenant_id, product_id=product_id)
    if product is None:
        raise LookupError("Product not found")
    return product


def get_warehouse(db: Session, *, tenant_id: str, warehouse_id: str) -> Branch | None:
    return db.scalar(
        select(Branch).where(
            Branch.id == warehouse_id,
            Branch.tenant_id == tenant_id,
            Branch.is_active.is_(True),
        )
    )


def require_warehouse(db: Session, *, tenant_id: str, warehouse_id: str) -> Branch:
    warehouse = get_warehouse(db, tenant_id=tenant_id, warehouse_id=warehouse_id)
    if warehouse is None:
        raise LookupError("Warehouse not found")
    return warehouse


def list_warehouses(
    db: Session,
    *,
    tenant_id: str,
    allowed_warehouse_ids: tuple[str, ...] | None,
) -> list[Branch]:
    stmt = select(Branch).where(
        Branch.tenant_id == tenant_id,
        Branch.is_active.is_(True),
    )
    if allowed_warehouse_ids is not None:
        stmt = stmt.where(Branch.id.in_(allowed_warehouse_ids))
    stmt = stmt.order_by(Branch.name.asc())
    return list(db.scalars(stmt))
