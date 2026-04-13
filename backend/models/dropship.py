"""Dropshipping Models - Suppliers, Sync, Auto-Fulfillment"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.database import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, index=True)
    website = Column(String(500), nullable=True)
    logo_url = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)

    # Contact
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(20), nullable=True)

    # API Integration
    api_endpoint = Column(String(500), nullable=True)
    api_key_encrypted = Column(String(500), nullable=True)
    sync_enabled = Column(Boolean, default=False)

    # Sync settings
    sync_interval_minutes = Column(Integer, default=60)
    auto_sync_price = Column(Boolean, default=True)
    auto_sync_stock = Column(Boolean, default=True)
    auto_sync_images = Column(Boolean, default=False)

    # Performance
    avg_lead_time_days = Column(Float, default=7.0)
    reliability_score = Column(Float, default=0.0)
    total_orders = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)

    # Status
    status = Column(String(20), default="active")  # active, paused, disabled
    is_verified = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_synced_at = Column(DateTime, nullable=True)

    products = relationship("Product")
    synced_products = relationship("SupplierSyncLog", back_populates="supplier")


class SupplierSyncLog(Base):
    __tablename__ = "supplier_sync_logs"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)

    sync_type = Column(String(20), nullable=False)  # full, price, stock, image, create, update
    status = Column(String(20), default="success")  # success, failed, partial
    items_synced = Column(Integer, default=0)
    items_failed = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    details = Column(JSON, default=dict)

    created_at = Column(DateTime, default=datetime.utcnow)
    duration_ms = Column(Integer, nullable=True)

    supplier = relationship("Supplier", back_populates="synced_products")


class SupplierMapping(Base):
    __tablename__ = "supplier_mappings"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    supplier_product_id = Column(String(200), nullable=False)
    supplier_product_url = Column(String(500), nullable=True)
    supplier_price = Column(Float, nullable=True)
    supplier_stock = Column(Integer, nullable=True)

    # Margin settings
    markup_type = Column(String(20), default="percentage")  # percentage, fixed
    markup_value = Column(Float, default=20.0)  # 20% markup or 20 VND fixed
    selling_price = Column(Float, nullable=True)

    # Auto-fulfillment
    auto_fulfill = Column(Boolean, default=False)
    fulfillment_status = Column(String(20), default="pending")

    last_synced_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    supplier = relationship("Supplier")
    product = relationship("Product")


class AutoFulfillmentOrder(Base):
    __tablename__ = "auto_fulfillment_orders"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    mapping_id = Column(Integer, ForeignKey("supplier_mappings.id"), nullable=False)

    supplier_order_id = Column(String(200), nullable=True)
    status = Column(String(20), default="pending")  # pending, submitted, confirmed, shipped, delivered, cancelled, failed
    tracking_number = Column(String(200), nullable=True)
    tracking_url = Column(String(500), nullable=True)

    # Cost
    supplier_cost = Column(Float, nullable=True)
    shipping_cost = Column(Float, default=0.0)
    total_cost = Column(Float, nullable=True)
    profit = Column(Float, nullable=True)

    # Timeline
    submitted_at = Column(DateTime, nullable=True)
    confirmed_at = Column(DateTime, nullable=True)
    shipped_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)

    error_message = Column(Text, nullable=True)
    gateway_response = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
