"""Cart Schemas"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = 1
    attributes: dict = {}


class CartItemUpdate(BaseModel):
    quantity: int
    attributes: dict = {}


class CartItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    attributes: dict
    product_name: str
    product_image: Optional[str]
    product_price: float
    product_slug: str
    stock_quantity: int
    subtotal: float
    added_at: datetime

    class Config:
        from_attributes = True


class CartResponse(BaseModel):
    id: int
    user_id: int
    items: List[CartItemResponse]
    total_items: int
    subtotal: float
    updated_at: datetime

    class Config:
        from_attributes = True


class WishlistAdd(BaseModel):
    product_id: int


class WishlistResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_image: Optional[str]
    product_price: float
    product_slug: str
    created_at: datetime

    class Config:
        from_attributes = True
