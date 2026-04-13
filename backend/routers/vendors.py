"""Vendor Router - Multi-vendor marketplace"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from pydantic import BaseModel

from backend.database import get_db
from backend.models.multi_vendor import Vendor, VendorPayout, VendorReview
from backend.models.user import User
from backend.models.product import Product
from backend.models.order import Order, OrderItem
from backend.core.auth import get_current_user_required, require_role

router = APIRouter(prefix="/api/vendors", tags=["Vendors"])


class VendorCreate(BaseModel):
    store_name: str
    store_description: str = ""
    contact_email: str = ""
    contact_phone: str = ""


class VendorResponse(BaseModel):
    id: int
    store_name: str
    store_slug: str
    status: str
    rating: float
    total_sales: int
    total_revenue: float

    class Config:
        from_attributes = True


@router.post("/register", response_model=VendorResponse)
async def register_vendor(data: VendorCreate, db: Session = Depends(get_db), user: dict = Depends(get_current_user_required)):
    existing = db.execute(select(Vendor).where(Vendor.user_id == user["id"])).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Already registered as vendor")

    # Upgrade user role
    db_user = db.get(User, user["id"])
    db_user.role = "vendor"

    vendor = Vendor(
        user_id=user["id"],
        store_name=data.store_name,
        store_slug=data.store_name.lower().replace(" ", "-"),
        store_description=data.store_description,
        contact_email=data.contact_email or user["email"],
        contact_phone=data.contact_phone,
        status="pending",
    )
    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    return VendorResponse.model_validate(vendor)


@router.get("/me", response_model=VendorResponse)
async def get_my_vendor(db: Session = Depends(get_db), user: dict = Depends(require_role("admin", "vendor"))):
    vendor = db.execute(select(Vendor).where(Vendor.user_id == user["id"])).scalar_one_or_none()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor profile not found")
    return VendorResponse.model_validate(vendor)


@router.get("/me/products")
async def get_vendor_products(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), db: Session = Depends(get_db), user: dict = Depends(require_role("admin", "vendor"))):
    vendor = db.execute(select(Vendor).where(Vendor.user_id == user["id"])).scalar_one_or_none()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    query = select(Product).where(Product.vendor_id == vendor.id)
    total = db.execute(select(func.count()).select_from(query.subquery())).scalar()
    products = db.execute(query.order_by(Product.created_at.desc()).offset((page-1)*page_size).limit(page_size)).scalars().all()
    return {"items": [{"id": p.id, "name": p.name, "price": p.price, "stock": p.stock_quantity, "status": p.status} for p in products], "total": total, "page": page, "page_size": page_size}


@router.get("/me/analytics")
async def get_vendor_analytics(db: Session = Depends(get_db), user: dict = Depends(require_role("admin", "vendor"))):
    vendor = db.execute(select(Vendor).where(Vendor.user_id == user["id"])).scalar_one_or_none()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    # Get vendor orders
    items = db.execute(select(OrderItem).where(OrderItem.vendor_id == vendor.id)).scalars().all()
    total_sales = len(items)
    total_revenue = sum(i.vendor_amount or 0 for i in items)
    pending_payout = sum(i.vendor_amount or 0 for i in items if i.payout_status == "pending")

    return {
        "total_sales": total_sales,
        "total_revenue": total_revenue,
        "pending_payout": pending_payout,
        "rating": vendor.rating,
        "review_count": vendor.review_count,
    }


@router.get("/me/payouts")
async def get_vendor_payouts(db: Session = Depends(get_db), user: dict = Depends(require_role("admin", "vendor"))):
    vendor = db.execute(select(Vendor).where(Vendor.user_id == user["id"])).scalar_one_or_none()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    payouts = db.execute(
        select(VendorPayout).where(VendorPayout.vendor_id == vendor.id).order_by(VendorPayout.created_at.desc())
    ).scalars().all()
    return [{"id": p.id, "amount": p.amount, "commission_amount": p.commission_amount, "net_amount": p.net_amount, "status": p.status, "created_at": p.created_at.isoformat()} for p in payouts]


@router.get("/{vendor_id}", response_model=VendorResponse)
async def get_vendor(vendor_id: int, db: Session = Depends(get_db)):
    vendor = db.get(Vendor, vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return VendorResponse.model_validate(vendor)


@router.get("")
async def list_vendors(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    query = select(Vendor).where(Vendor.status == "approved")
    total = db.execute(select(func.count()).select_from(query.subquery())).scalar()
    vendors = db.execute(query.order_by(Vendor.rating.desc()).offset((page-1)*page_size).limit(page_size)).scalars().all()
    return {"items": [VendorResponse.model_validate(v) for v in vendors], "total": total, "page": page, "page_size": page_size}
