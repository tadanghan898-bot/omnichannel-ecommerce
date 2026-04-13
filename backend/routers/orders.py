"""Orders Router"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_
from typing import Optional
import uuid, math

from backend.database import get_db
from backend.models.order import Order, OrderItem, Coupon, ShippingMethod
from backend.models.product import Product, InventoryLog
from backend.models.cart import Cart, CartItem
from backend.models.payment import Payment
from backend.schemas.order import OrderCreate, OrderResponse, OrderDetailResponse, OrderListResponse, CouponCreate, CouponResponse
from backend.core.auth import get_current_user_required, require_role

router = APIRouter(prefix="/api/orders", tags=["Orders"])


def generate_order_number():
    return f"ORD-{uuid.uuid4().hex[:8].upper()}"


@router.post("", response_model=OrderResponse)
async def create_order(data: OrderCreate, db: Session = Depends(get_db), user: dict = Depends(get_current_user_required)):
    # Get cart items
    cart_items = db.execute(
        select(CartItem).where(CartItem.user_id == user["id"])
    ).scalars().all()

    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    # Build order items
    subtotal = 0.0
    order_items = []
    for ci in cart_items:
        product = db.get(Product, ci.product_id)
        if not product or product.status != "active":
            continue
        if product.stock_quantity < ci.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for {product.name}")

        item_total = product.price * ci.quantity
        subtotal += item_total

        order_items.append({
            "product_id": product.id,
            "name": product.name,
            "sku": product.sku,
            "quantity": ci.quantity,
            "unit_price": product.price,
            "total_price": item_total,
            "attributes": ci.attributes,
        })

        # Reduce stock
        product.stock_quantity -= ci.quantity
        log = InventoryLog(
            product_id=product.id,
            change_type="sale",
            quantity_change=-ci.quantity,
            previous_quantity=product.stock_quantity + ci.quantity,
            new_quantity=product.stock_quantity,
            reason=f"Order created"
        )
        db.add(log)

    if not order_items:
        raise HTTPException(status_code=400, detail="No valid items")

    # Apply coupon
    discount = 0.0
    coupon = None
    if data.coupon_code:
        coupon = db.execute(select(Coupon).where(Coupon.code == data.coupon_code)).scalar_one_or_none()
        if coupon and coupon.is_active:
            if coupon.min_order_amount <= subtotal:
                if coupon.type == "percentage":
                    discount = subtotal * (coupon.value / 100)
                    if coupon.max_discount_amount:
                        discount = min(discount, coupon.max_discount_amount)
                else:
                    discount = coupon.value
                coupon.used_count += 1

    # Calculate total
    shipping = data.shipping_method or "standard"
    shipping_amount = 0.0
    if shipping == "express":
        shipping_amount = 50000.0

    total = subtotal - discount + shipping_amount

    # Create order
    order = Order(
        order_number=generate_order_number(),
        user_id=user["id"],
        subtotal=subtotal,
        discount_amount=discount,
        shipping_amount=shipping_amount,
        total=total,
        coupon_id=coupon.id if coupon else None,
        coupon_code=data.coupon_code,
        shipping_name=data.shipping_name,
        shipping_phone=data.shipping_phone,
        shipping_address=data.shipping_address,
        shipping_city=data.shipping_city,
        shipping_postal_code=data.shipping_postal_code,
        shipping_country=data.shipping_country,
        shipping_method=shipping,
        payment_method=data.payment_method,
        customer_note=data.customer_note,
        status="pending",
        payment_status="pending",
    )
    db.add(order)
    db.flush()

    # Create order items
    for item in order_items:
        oi = OrderItem(order_id=order.id, **item)
        db.add(oi)

    # Clear cart
    db.execute(select(CartItem).where(CartItem.user_id == user["id"]).delete())

    # Create payment record
    payment = Payment(
        order_id=order.id,
        user_id=user["id"],
        amount=total,
        method=data.payment_method,
        status="pending",
    )
    db.add(payment)

    db.commit()
    db.refresh(order)
    return OrderResponse.model_validate(order)


@router.get("", response_model=OrderListResponse)
async def list_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user_required),
):
    query = select(Order).where(Order.user_id == user["id"])
    if status:
        query = query.where(Order.status == status)

    total = db.execute(select(func.count()).select_from(query.subquery())).scalar()
    orders = db.execute(query.order_by(Order.created_at.desc()).offset((page-1)*page_size).limit(page_size)).scalars().all()

    return OrderListResponse(
        items=[OrderResponse.model_validate(o) for o in orders],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{order_id}", response_model=OrderDetailResponse)
async def get_order(order_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user_required)):
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.user_id != user["id"] and user["role"] not in ["admin", "vendor"]:
        raise HTTPException(status_code=403, detail="Access denied")

    items = db.execute(select(OrderItem).where(OrderItem.order_id == order_id)).scalars().all()
    resp = OrderDetailResponse.model_validate(order)
    resp.items = [OrderItem.model_validate(i) for i in items]
    return resp


@router.post("/{order_id}/cancel")
async def cancel_order(order_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user_required)):
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.user_id != user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    if order.status not in ["pending", "confirmed"]:
        raise HTTPException(status_code=400, detail="Cannot cancel this order")

    # Restore stock
    items = db.execute(select(OrderItem).where(OrderItem.order_id == order_id)).scalars().all()
    for item in items:
        product = db.get(Product, item.product_id)
        if product:
            product.stock_quantity += item.quantity
            db.add(InventoryLog(
                product_id=product.id,
                change_type="return",
                quantity_change=item.quantity,
                previous_quantity=product.stock_quantity - item.quantity,
                new_quantity=product.stock_quantity,
                order_id=order_id,
            ))

    order.status = "cancelled"
    order.cancelled_at = func.now()
    db.commit()
    return {"message": "Order cancelled"}


# Admin: Order management
@router.get("/admin/all", response_model=OrderListResponse)
async def admin_list_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("admin")),
):
    query = select(Order)
    if status:
        query = query.where(Order.status == status)
    total = db.execute(select(func.count()).select_from(query.subquery())).scalar()
    orders = db.execute(query.order_by(Order.created_at.desc()).offset((page-1)*page_size).limit(page_size)).scalars().all()
    return OrderListResponse(items=[OrderResponse.model_validate(o) for o in orders], total=total, page=page, page_size=page_size)


@router.put("/admin/{order_id}/status")
async def admin_update_order_status(order_id: int, status: str, tracking_number: Optional[str] = None, db: Session = Depends(get_db), user: dict = Depends(require_role("admin"))):
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = status
    if tracking_number:
        order.tracking_number = tracking_number

    if status == "shipped":
        order.shipped_at = func.now()
    elif status == "delivered":
        order.delivered_at = func.now()
        order.fulfillment_status = "fulfilled"

    db.commit()
    return {"message": f"Order status updated to {status}"}
