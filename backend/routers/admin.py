"""Admin Dashboard Router"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta

from backend.database import get_db
from backend.models.user import User
from backend.models.product import Product
from backend.models.order import Order, OrderItem
from backend.models.payment import Payment
from backend.core.auth import require_role

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/dashboard")
async def get_dashboard_stats(db: Session = Depends(get_db), user: dict = Depends(require_role("admin"))):
    # Counts
    total_users = db.execute(select(func.count()).select_from(User)).scalar() or 0
    total_products = db.execute(select(func.count()).select_from(Product)).scalar() or 0
    total_orders = db.execute(select(func.count()).select_from(Order)).scalar() or 0
    total_revenue = db.execute(select(func.sum(Order.total)).select_from(Order).where(Order.payment_status == "paid")).scalar() or 0

    # Orders by status
    orders_by_status = {}
    for status in ["pending", "confirmed", "processing", "shipped", "delivered", "cancelled"]:
        count = db.execute(select(func.count()).select_from(Order).where(Order.status == status)).scalar() or 0
        orders_by_status[status] = count

    # Recent orders
    recent_orders = db.execute(
        select(Order).order_by(Order.created_at.desc()).limit(10)
    ).scalars().all()

    # Top products
    top_products = db.execute(
        select(Product).where(
            and_(Product.status == "active", Product.is_bestseller == True)
        ).limit(10)
    ).scalars().all()

    return {
        "stats": {
            "total_users": total_users,
            "total_products": total_products,
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "orders_by_status": orders_by_status,
        },
        "recent_orders": [
            {"id": o.id, "order_number": o.order_number, "total": o.total, "status": o.status, "created_at": o.created_at.isoformat()}
            for o in recent_orders
        ],
        "top_products": [
            {"id": p.id, "name": p.name, "price": p.price, "stock": p.stock_quantity, "rating": p.rating}
            for p in top_products
        ],
    }


@router.get("/users")
async def admin_list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    role: str = None,
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("admin")),
):
    query = select(User)
    if role:
        query = query.where(User.role == role)
    total = db.execute(select(func.count()).select_from(query.subquery())).scalar()
    users = db.execute(query.order_by(User.created_at.desc()).offset((page-1)*page_size).limit(page_size)).scalars().all()
    return {"items": [{"id": u.id, "email": u.email, "role": u.role, "is_active": u.is_active, "created_at": u.created_at.isoformat()} for u in users], "total": total, "page": page, "page_size": page_size}


@router.put("/users/{user_id}/role")
async def admin_update_user_role(user_id: int, role: str, db: Session = Depends(get_db), user: dict = Depends(require_role("admin"))):
    target = db.get(User, user_id)
    if not target:
        return {"error": "User not found"}
    target.role = role
    db.commit()
    return {"message": f"User role updated to {role}"}


@router.get("/analytics")
async def get_analytics(days: int = Query(30, ge=1, le=365), db: Session = Depends(get_db), user: dict = Depends(require_role("admin"))):
    since = datetime.utcnow() - timedelta(days=days)

    # Orders over time
    orders = db.execute(
        select(Order).where(Order.created_at >= since)
    ).scalars().all()

    daily_data = {}
    for o in orders:
        day = o.created_at.date().isoformat()
        if day not in daily_data:
            daily_data[day] = {"orders": 0, "revenue": 0}
        daily_data[day]["orders"] += 1
        if o.payment_status == "paid":
            daily_data[day]["revenue"] += o.total

    return {
        "period_days": days,
        "total_orders": len(orders),
        "total_revenue": sum(o.total for o in orders if o.payment_status == "paid"),
        "daily_data": daily_data,
    }
