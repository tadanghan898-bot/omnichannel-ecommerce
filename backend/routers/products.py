"""Products Router - CRUD, Search, Categories, Reviews"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_, and_
from typing import Optional, List
import math

from backend.database import get_db
from backend.models.product import Product, Category, Brand, Review, WishlistItem, InventoryLog
from backend.schemas.product import (
    ProductCreate, ProductUpdate, ProductResponse, ProductListResponse,
    CategoryCreate, CategoryResponse,
    BrandCreate, BrandResponse,
    ReviewCreate, ReviewResponse
)
from backend.core.auth import get_current_user, get_current_user_required, require_role

router = APIRouter(prefix="/api/products", tags=["Products"])


# === CATEGORIES ===
@router.get("/categories", response_model=list[CategoryResponse])
async def list_categories(db: Session = Depends(get_db)):
    cats = db.execute(select(Category).where(Category.is_active == True).order_by(Category.sort_order)).scalars().all()
    return [CategoryResponse.model_validate(c) for c in cats]


@router.post("/categories", response_model=CategoryResponse)
async def create_category(data: CategoryCreate, db: Session = Depends(get_db), user: dict = Depends(require_role("admin"))):
    cat = Category(**data.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return CategoryResponse.model_validate(cat)


# === BRANDS ===
@router.get("/brands", response_model=list[BrandResponse])
async def list_brands(db: Session = Depends(get_db)):
    brands = db.execute(select(Brand).where(Brand.is_active == True)).scalars().all()
    return [BrandResponse.model_validate(b) for b in brands]


@router.post("/brands", response_model=BrandResponse)
async def create_brand(data: BrandCreate, db: Session = Depends(get_db), user: dict = Depends(require_role("admin", "vendor"))):
    brand = Brand(**data.model_dump())
    db.add(brand)
    db.commit()
    db.refresh(brand)
    return BrandResponse.model_validate(brand)


# === PRODUCTS ===
@router.get("", response_model=ProductListResponse)
async def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category_id: Optional[int] = None,
    brand_id: Optional[int] = None,
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    featured: Optional[bool] = None,
    bestseller: Optional[bool] = None,
    vendor_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    query = select(Product).where(Product.status == "active")

    if search:
        query = query.where(or_(
            Product.name.ilike(f"%{search}%"),
            Product.description.ilike(f"%{search}%"),
            Product.tags.ilike(f"%{search}%")
        ))
    if category_id:
        query = query.where(Product.category_id == category_id)
    if brand_id:
        query = query.where(Product.brand_id == brand_id)
    if vendor_id:
        query = query.where(Product.vendor_id == vendor_id)
    if min_price is not None:
        query = query.where(Product.price >= min_price)
    if max_price is not None:
        query = query.where(Product.price <= max_price)
    if featured:
        query = query.where(Product.is_featured == True)
    if bestseller:
        query = query.where(Product.is_bestseller == True)

    # Count total
    total = db.execute(select(func.count()).select_from(query.subquery())).scalar()

    # Sort
    sort_column = getattr(Product, sort_by, Product.created_at)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Paginate
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    products = db.execute(query).scalars().all()
    pages = math.ceil(total / page_size) if total > 0 else 1

    return ProductListResponse(
        items=[ProductResponse.model_validate(p) for p in products],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get("/featured", response_model=list[ProductResponse])
async def get_featured_products(limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db)):
    products = db.execute(
        select(Product).where(
            and_(Product.status == "active", Product.is_featured == True)
        ).order_by(Product.created_at.desc()).limit(limit)
    ).scalars().all()
    return [ProductResponse.model_validate(p) for p in products]


@router.get("/bestsellers", response_model=list[ProductResponse])
async def get_bestsellers(limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db)):
    products = db.execute(
        select(Product).where(
            and_(Product.status == "active", Product.is_bestseller == True)
        ).order_by(Product.rating.desc()).limit(limit)
    ).scalars().all()
    return [ProductResponse.model_validate(p) for p in products]


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product or product.status == "deleted":
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductResponse.model_validate(product)


@router.get("/slug/{slug}", response_model=ProductResponse)
async def get_product_by_slug(slug: str, db: Session = Depends(get_db)):
    product = db.execute(select(Product).where(Product.slug == slug)).scalar_one_or_none()
    if not product or product.status == "deleted":
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductResponse.model_validate(product)


@router.post("", response_model=ProductResponse)
async def create_product(data: ProductCreate, db: Session = Depends(get_db), user: dict = Depends(require_role("admin", "vendor"))):
    kwargs = data.model_dump()
    if user["role"] == "vendor":
        kwargs["vendor_id"] = user.get("vendor_id")
    product = Product(**kwargs)
    db.add(product)
    db.commit()
    db.refresh(product)
    return ProductResponse.model_validate(product)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(product_id: int, data: ProductUpdate, db: Session = Depends(get_db), user: dict = Depends(require_role("admin", "vendor"))):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Vendors can only edit their own products
    if user["role"] == "vendor" and product.vendor_id != user.get("vendor_id"):
        raise HTTPException(status_code=403, detail="Not your product")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return ProductResponse.model_validate(product)


@router.delete("/{product_id}")
async def delete_product(product_id: int, db: Session = Depends(get_db), user: dict = Depends(require_role("admin"))):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.status = "deleted"
    db.commit()
    return {"message": "Product deleted"}


# === REVIEWS ===
@router.get("/{product_id}/reviews", response_model=list[ReviewResponse])
async def get_product_reviews(product_id: int, page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=50), db: Session = Depends(get_db)):
    reviews = db.execute(
        select(Review).where(
            and_(Review.product_id == product_id, Review.is_approved == True)
        ).order_by(Review.created_at.desc()).offset((page-1)*page_size).limit(page_size)
    ).scalars().all()

    result = []
    for r in reviews:
        user_obj = db.get(User, r.user_id)
        resp = ReviewResponse.model_validate(r)
        resp.user_name = user_obj.full_name if user_obj else "Anonymous"
        result.append(resp)
    return result


from backend.models.user import User


@router.post("/{product_id}/reviews", response_model=ReviewResponse)
async def create_review(product_id: int, data: ReviewCreate, db: Session = Depends(get_db), user: dict = Depends(get_current_user_required)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    review = Review(
        product_id=product_id,
        user_id=user["id"],
        **data.model_dump()
    )
    db.add(review)

    # Update product rating
    all_reviews = db.execute(select(func.avg(Review.rating), func.count()).where(Review.product_id == product_id)).one()
    product.rating = float(all_reviews[0] or 0)
    product.review_count = all_reviews[1] or 0

    db.commit()
    db.refresh(review)
    return ReviewResponse.model_validate(review)
