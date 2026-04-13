"""Multi-Tenant / SaaS Router"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from pydantic import BaseModel

from backend.database import get_db
from backend.models.multi_tenant import Tenant, TenantUser, SubscriptionPlan
from backend.models.user import User
from backend.core.auth import require_role, get_current_user_required
from backend.core.config import is_module_active

router = APIRouter(prefix="/api/tenants", tags=["Multi-Tenant SaaS"])


class TenantCreate(BaseModel):
    name: str
    subdomain: str
    plan: str = "free"


@router.get("/plans")
async def list_plans(db: Session = Depends(get_db)):
    plans = db.execute(select(SubscriptionPlan).where(SubscriptionPlan.is_active == True).order_by(SubscriptionPlan.monthly_price)).scalars().all()
    return [{"id": p.id, "name": p.name, "slug": p.slug, "monthly_price": p.monthly_price, "yearly_price": p.yearly_price, "max_products": p.max_products, "features": p.features} for p in plans]


@router.post("", response_model=dict)
async def create_tenant(data: TenantCreate, db: Session = Depends(get_db), user: dict = Depends(get_current_user_required)):
    if not is_module_active("multi_tenant"):
        raise HTTPException(status_code=403, detail="Multi-tenant module not active")

    existing = db.execute(select(Tenant).where(Tenant.subdomain == data.subdomain)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Subdomain taken")

    # Upgrade user role
    db_user = db.get(User, user["id"])
    db_user.role = "admin"

    tenant = Tenant(
        name=data.name,
        subdomain=data.subdomain,
        slug=data.subdomain,
        owner_user_id=user["id"],
        plan=data.plan,
    )
    db.add(tenant)
    db.flush()

    # Add owner as tenant admin
    tu = TenantUser(tenant_id=tenant.id, user_id=user["id"], role="owner")
    db.add(tu)

    db.commit()
    return {"id": tenant.id, "subdomain": tenant.subdomain, "message": "Store created"}


@router.get("/me")
async def get_my_tenant(db: Session = Depends(get_db), user: dict = Depends(get_current_user_required)):
    tenant_user = db.execute(select(TenantUser).where(TenantUser.user_id == user["id"])).scalar_one_or_none()
    if not tenant_user:
        raise HTTPException(status_code=404, detail="No store found")
    tenant = db.get(Tenant, tenant_user.tenant_id)
    return {"id": tenant.id, "name": tenant.name, "subdomain": tenant.subdomain, "plan": tenant.plan, "subscription_status": tenant.subscription_status}
