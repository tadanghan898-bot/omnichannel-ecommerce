"""Cart Router"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from backend.database import get_db
from backend.models.cart import Cart, CartItem
from backend.models.product import Product, WishlistItem
from backend.schemas.cart import CartItemCreate, CartItemUpdate, CartItemResponse, CartResponse, WishlistAdd, WishlistResponse
from backend.core.auth import get_current_user, get_current_user_required

router = APIRouter(prefix="/api/cart", tags=["Cart"])


def get_or_create_cart(db: Session, user_id: int) -> Cart:
    cart = db.execute(select(Cart).where(Cart.user_id == user_id)).scalar_one_or_none()
    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart


def build_cart_response(db: Session, cart: Cart) -> CartResponse:
    items = db.execute(select(CartItem).where(CartItem.cart_id == cart.id)).scalars().all()
    resp_items = []
    total = 0
    count = 0
    for ci in items:
        product = db.get(Product, ci.product_id)
        if not product:
            continue
        item_total = product.price * ci.quantity
        count += ci.quantity
        total += item_total
        resp_items.append(CartItemResponse(
            id=ci.id,
            product_id=ci.product_id,
            quantity=ci.quantity,
            attributes=ci.attributes,
            product_name=product.name,
            product_image=product.thumbnail_url,
            product_price=product.price,
            product_slug=product.slug,
            stock_quantity=product.stock_quantity,
            subtotal=item_total,
            added_at=ci.added_at,
        ))

    return CartResponse(
        id=cart.id,
        user_id=cart.user_id,
        items=resp_items,
        total_items=count,
        subtotal=total,
        updated_at=cart.updated_at,
    )


@router.get("", response_model=CartResponse)
async def get_cart(db: Session = Depends(get_db), user: dict = Depends(get_current_user_required)):
    cart = get_or_create_cart(db, user["id"])
    return build_cart_response(db, cart)


@router.post("/items", response_model=CartResponse)
async def add_to_cart(data: CartItemCreate, db: Session = Depends(get_db), user: dict = Depends(get_current_user_required)):
    product = db.get(Product, data.product_id)
    if not product or product.status != "active":
        raise HTTPException(status_code=404, detail="Product not found")

    cart = get_or_create_cart(db, user["id"])

    # Check if item already in cart
    existing = db.execute(
        select(CartItem).where(
            and_(
                CartItem.cart_id == cart.id,
                CartItem.product_id == data.product_id,
            )
        )
    ).scalar_one_or_none()

    if existing:
        existing.quantity += data.quantity
    else:
        item = CartItem(
            cart_id=cart.id,
            user_id=user["id"],
            product_id=data.product_id,
            quantity=data.quantity,
            attributes=data.attributes,
        )
        db.add(item)

    db.commit()
    return build_cart_response(db, cart)


@router.put("/items/{item_id}", response_model=CartResponse)
async def update_cart_item(item_id: int, data: CartItemUpdate, db: Session = Depends(get_db), user: dict = Depends(get_current_user_required)):
    item = db.get(CartItem, item_id)
    if not item or item.user_id != user["id"]:
        raise HTTPException(status_code=404, detail="Item not found")

    item.quantity = data.quantity
    db.commit()
    return build_cart_response(db, db.get(Cart, item.cart_id))


@router.delete("/items/{item_id}", response_model=CartResponse)
async def remove_cart_item(item_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user_required)):
    item = db.get(CartItem, item_id)
    if not item or item.user_id != user["id"]:
        raise HTTPException(status_code=404, detail="Item not found")
    cart_id = item.cart_id
    db.delete(item)
    db.commit()
    return build_cart_response(db, db.get(Cart, cart_id))


@router.delete("", response_model=CartResponse)
async def clear_cart(db: Session = Depends(get_db), user: dict = Depends(get_current_user_required)):
    cart = get_or_create_cart(db, user["id"])
    db.execute(select(CartItem).where(CartItem.cart_id == cart.id).delete())
    db.commit()
    return build_cart_response(db, cart)


# === WISHLIST ===
@router.get("/wishlist", response_model=list[WishlistResponse])
async def get_wishlist(db: Session = Depends(get_db), user: dict = Depends(get_current_user_required)):
    items = db.execute(select(WishlistItem).where(WishlistItem.user_id == user["id"])).scalars().all()
    result = []
    for item in items:
        product = db.get(Product, item.product_id)
        if product:
            result.append(WishlistResponse(
                id=item.id,
                product_id=item.product_id,
                product_name=product.name,
                product_image=product.thumbnail_url,
                product_price=product.price,
                product_slug=product.slug,
                created_at=item.created_at,
            ))
    return result


@router.post("/wishlist", response_model=WishlistResponse)
async def add_to_wishlist(data: WishlistAdd, db: Session = Depends(get_db), user: dict = Depends(get_current_user_required)):
    existing = db.execute(select(WishlistItem).where(WishlistItem.user_id == user["id"], WishlistItem.product_id == data.product_id)).scalar_one_or_none()
    if existing:
        return WishlistResponse(id=existing.id, product_id=existing.product_id, created_at=existing.created_at)

    product = db.get(Product, data.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    item = WishlistItem(user_id=user["id"], product_id=data.product_id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return WishlistResponse(
        id=item.id,
        product_id=item.product_id,
        product_name=product.name,
        product_image=product.thumbnail_url,
        product_price=product.price,
        product_slug=product.slug,
        created_at=item.created_at,
    )


@router.delete("/wishlist/{product_id}")
async def remove_from_wishlist(product_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user_required)):
    item = db.execute(select(WishlistItem).where(WishlistItem.user_id == user["id"], WishlistItem.product_id == product_id)).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item not in wishlist")
    db.delete(item)
    db.commit()
    return {"message": "Removed from wishlist"}
