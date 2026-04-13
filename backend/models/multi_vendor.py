"""Multi-Vendor / Marketplace Models"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.database import Base


class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    store_name = Column(String(200), nullable=False)
    store_slug = Column(String(200), unique=True, index=True)
    store_description = Column(Text, nullable=True)
    logo_url = Column(String(500), nullable=True)
    banner_url = Column(String(500), nullable=True)

    # Contact
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)

    # Status
    status = Column(String(20), default="pending")  # pending, approved, suspended, rejected
    is_verified = Column(Boolean, default=False)
    rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    total_sales = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)

    # Commission
    commission_rate = Column(Float, default=10.0)  # 10% default
    custom_commission = Column(Boolean, default=False)

    # Payout
    payout_method = Column(String(50), nullable=True)
    payout_email = Column(String(255), nullable=True)
    payout_info = Column(JSON, default=dict)

    # Social
    facebook_url = Column(String(500), nullable=True)
    instagram_url = Column(String(500), nullable=True)
    website_url = Column(String(500), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="vendor_profile")
    products = relationship("Product", back_populates="vendor")
    vendor_orders = relationship("VendorPayout", back_populates="vendor")
    reviews = relationship("VendorReview", back_populates="vendor")


class VendorPayout(Base):
    __tablename__ = "vendor_payouts"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    period_start = Column(DateTime, nullable=True)
    period_end = Column(DateTime, nullable=True)

    amount = Column(Float, nullable=False)
    commission_amount = Column(Float, default=0.0)
    net_amount = Column(Float, nullable=False)

    status = Column(String(20), default="pending")  # pending, approved, paid, failed
    payment_method = Column(String(50), nullable=True)
    transaction_id = Column(String(200), nullable=True)
    paid_at = Column(DateTime, nullable=True)

    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    vendor = relationship("Vendor", back_populates="vendor_orders")
    order = relationship("Order", back_populates="vendor_payouts")


class VendorReview(Base):
    __tablename__ = "vendor_reviews"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)

    rating = Column(Integer, nullable=False)  # 1-5
    comment = Column(Text, nullable=True)
    is_approved = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    vendor = relationship("Vendor", back_populates="reviews")
