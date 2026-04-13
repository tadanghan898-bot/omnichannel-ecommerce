"""Order Schemas"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int
    attributes: dict = {}


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    name: str
    sku: Optional[str]
    quantity: int
    unit_price: float
    total_price: float
    attributes: dict

    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    items: List[OrderItemCreate]
    shipping_name: str
    shipping_phone: str
    shipping_address: str
    shipping_city: str
    shipping_postal_code: Optional[str] = None
    shipping_country: str = "Vietnam"
    shipping_method: Optional[str] = None
    coupon_code: Optional[str] = None
    payment_method: str = "cod"
    customer_note: Optional[str] = None


class OrderResponse(BaseModel):
    id: int
    order_number: str
    user_id: int
    status: str
    fulfillment_status: str
    payment_status: str
    subtotal: float
    discount_amount: float
    shipping_amount: float
    tax_amount: float
    total: float
    currency: str
    payment_method: Optional[str]
    tracking_number: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OrderDetailResponse(OrderResponse):
    items: List[OrderItemResponse]

    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    items: List[OrderResponse]
    total: int
    page: int
    page_size: int


class CouponCreate(BaseModel):
    code: str
    type: str = "percentage"
    value: float
    min_order_amount: float = 0.0
    max_discount_amount: Optional[float] = None
    usage_limit: Optional[int] = None
    per_user_limit: int = 1
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class CouponResponse(CouponCreate):
    id: int
    used_count: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PaymentIntentCreate(BaseModel):
    amount: float
    currency: str = "VND"
    method: str = "stripe"


class PaymentIntentResponse(BaseModel):
    client_secret: str
    payment_intent_id: str
    amount: float
    currency: str
