"""Order, OrderItem, and Shipping Models"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)  # multi_tenant

    # Status
    status = Column(String(30), default="pending")  # pending, confirmed, processing, shipped, delivered, cancelled, refunded
    fulfillment_status = Column(String(30), default="unfulfilled")
    payment_status = Column(String(30), default="pending")  # pending, paid, failed, refunded, partially_refunded

    # Pricing
    subtotal = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    shipping_amount = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    total = Column(Float, default=0.0)
    currency = Column(String(10), default="VND")

    # Shipping
    shipping_name = Column(String(200), nullable=True)
    shipping_phone = Column(String(20), nullable=True)
    shipping_address = Column(Text, nullable=True)
    shipping_city = Column(String(100), nullable=True)
    shipping_postal_code = Column(String(20), nullable=True)
    shipping_country = Column(String(100), nullable=True)
    shipping_method = Column(String(100), nullable=True)
    tracking_number = Column(String(200), nullable=True)
    tracking_url = Column(String(500), nullable=True)

    # Customer notes
    customer_note = Column(Text, nullable=True)
    internal_note = Column(Text, nullable=True)

    # Coupon
    coupon_code = Column(String(50), nullable=True)
    coupon_id = Column(Integer, ForeignKey("coupons.id"), nullable=True)

    # Payment
    payment_method = Column(String(50), nullable=True)
    payment_id = Column(String(200), nullable=True)  # external payment reference
    paid_at = Column(DateTime, nullable=True)

    # Refunds
    refunded_amount = Column(Float, default=0.0)
    refund_reason = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    confirmed_at = Column(DateTime, nullable=True)
    shipped_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    coupon = relationship("Coupon")
    payment = relationship("Payment", back_populates="order", uselist=False)
    vendor_payouts = relationship("VendorPayout", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=True)  # multi_vendor

    name = Column(String(500), nullable=False)
    sku = Column(String(100), nullable=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)

    # Vendor payout info (multi_vendor)
    vendor_amount = Column(Float, nullable=True)
    commission_amount = Column(Float, nullable=True)
    commission_rate = Column(Float, nullable=True)
    payout_status = Column(String(30), default="pending")

    # Attributes
    attributes = Column(JSON, default=dict)  # {"color": "red", "size": "M"}

    # Fulfillment
    fulfillment_status = Column(String(30), default="unfulfilled")
    shipped_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")


class Coupon(Base):
    __tablename__ = "coupons"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    type = Column(String(20), default="percentage")  # percentage, fixed_amount, free_shipping
    value = Column(Float, nullable=False)
    min_order_amount = Column(Float, default=0.0)
    max_discount_amount = Column(Float, nullable=True)
    usage_limit = Column(Integer, nullable=True)
    used_count = Column(Integer, default=0)
    per_user_limit = Column(Integer, default=1)

    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    applicable_products = Column(JSON, default=list)  # product IDs
    applicable_categories = Column(JSON, default=list)  # category IDs

    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    tenant = relationship("Tenant")


class ShippingMethod(Base):
    __tablename__ = "shipping_methods"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, default=0.0)
    estimated_days = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    tenant = relationship("Tenant")
