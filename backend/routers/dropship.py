"""Dropshipping Router"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from pydantic import BaseModel
from typing import Optional

from backend.database import get_db
from backend.models.dropship import Supplier, SupplierSyncLog, SupplierMapping, AutoFulfillmentOrder
from backend.models.product import Product
from backend.core.auth import require_role, get_current_user_required
from backend.core.config import is_module_active

router = APIRouter(prefix="/api/dropship", tags=["Dropshipping"])


class SupplierCreate(BaseModel):
    name: str
    website: str = ""
    description: str = ""
    api_endpoint: str = ""
    sync_enabled: bool = False


class SupplierMappingCreate(BaseModel):
    supplier_id: int
    supplier_product_id: str
    supplier_product_url: str = ""
    markup_type: str = "percentage"
    markup_value: float = 20.0
    auto_fulfill: bool = False


@router.get("/suppliers", response_model=list)
async def list_suppliers(db: Session = Depends(get_db), user: dict = Depends(require_role("admin", "vendor"))):
    suppliers = db.execute(select(Supplier).where(Supplier.status == "active")).scalars().all()
    return [{"id": s.id, "name": s.name, "website": s.website, "total_products": s.total_orders, "reliability_score": s.reliability_score} for s in suppliers]


@router.post("/suppliers", response_model=dict)
async def create_supplier(data: SupplierCreate, db: Session = Depends(get_db), user: dict = Depends(require_role("admin"))):
    supplier = Supplier(**data.model_dump())
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return {"id": supplier.id, "name": supplier.name, "status": supplier.status}


@router.post("/map", response_model=dict)
async def create_supplier_mapping(data: SupplierMappingCreate, db: Session = Depends(get_db), user: dict = Depends(require_role("admin", "vendor"))):
    mapping = SupplierMapping(**data.model_dump())
    db.add(mapping)
    db.commit()
    return {"id": mapping.id, "status": "mapped"}


@router.get("/products/import")
async def import_supplier_products(
    supplier_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("admin", "vendor")),
):
    if not is_module_active("dropship"):
        raise HTTPException(status_code=403, detail="Dropship module not active")

    supplier = db.get(Supplier, supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    # Mock: In production, fetch from supplier API
    return {
        "supplier_id": supplier_id,
        "supplier_name": supplier.name,
        "products_found": 0,
        "message": "In production, this would fetch products from the supplier's API and create Product records.",
    }


@router.post("/sync/{supplier_id}")
async def sync_supplier(supplier_id: int, db: Session = Depends(get_db), user: dict = Depends(require_role("admin"))):
    if not is_module_active("dropship"):
        raise HTTPException(status_code=403, detail="Dropship module not active")

    supplier = db.get(Supplier, supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    log = SupplierSyncLog(supplier_id=supplier_id, sync_type="full", status="success", items_synced=0)
    db.add(log)
    supplier.last_synced_at = func.now()
    db.commit()
    return {"message": f"Synced with {supplier.name}", "items_synced": 0}


@router.get("/orders/fulfillment")
async def get_fulfillment_orders(db: Session = Depends(get_db), user: dict = Depends(require_role("admin"))):
    orders = db.execute(
        select(AutoFulfillmentOrder).order_by(AutoFulfillmentOrder.created_at.desc()).limit(50)
    ).scalars().all()
    return [{"id": o.id, "status": o.status, "supplier_cost": o.supplier_cost, "profit": o.profit, "created_at": o.created_at.isoformat()} for o in orders]
