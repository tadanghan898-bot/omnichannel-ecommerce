"""Product Schemas"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class CategoryBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    parent_id: Optional[int] = None
    sort_order: int = 0


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class BrandBase(BaseModel):
    name: str
    slug: str
    logo_url: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None


class BrandCreate(BrandBase):
    pass


class BrandResponse(BrandBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    short_description: Optional[str] = None
    price: float
    compare_at_price: Optional[float] = None
    cost_price: Optional[float] = None
    stock_quantity: int = 0
    images: List[dict] = []
    thumbnail_url: Optional[str] = None
    category_id: Optional[int] = None
    brand_id: Optional[int] = None
    tags: List[str] = []
    attributes: dict = {}
    weight: Optional[float] = None
    is_featured: bool = False
    is_bestseller: bool = False


class ProductCreate(ProductBase):
    sku: Optional[str] = None
    vendor_id: Optional[int] = None
    tenant_id: Optional[int] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    compare_at_price: Optional[float] = None
    stock_quantity: Optional[int] = None
    images: Optional[List[dict]] = None
    thumbnail_url: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    attributes: Optional[dict] = None
    is_featured: Optional[bool] = None
    is_bestseller: Optional[bool] = None


class ProductResponse(ProductBase):
    id: int
    sku: Optional[str]
    vendor_id: Optional[int]
    status: str
    rating: float
    review_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    items: List[ProductResponse]
    total: int
    page: int
    page_size: int
    pages: int


class ReviewCreate(BaseModel):
    rating: int
    title: Optional[str] = None
    comment: Optional[str] = None
    images: List[str] = []


class ReviewResponse(BaseModel):
    id: int
    product_id: int
    user_id: int
    rating: int
    title: Optional[str]
    comment: Optional[str]
    images: List[dict]
    is_verified_purchase: bool
    helpful_count: int
    created_at: datetime
    user_name: Optional[str] = None

    class Config:
        from_attributes = True
