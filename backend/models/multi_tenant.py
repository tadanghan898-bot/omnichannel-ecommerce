"""Multi-Tenant / SaaS Platform Models"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.database import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, index=True)
    subdomain = Column(String(100), unique=True, nullable=True)

    # Branding
    logo_url = Column(String(500), nullable=True)
    favicon_url = Column(String(500), nullable=True)
    primary_color = Column(String(20), default="#6366f1")
    secondary_color = Column(String(20), default="#8b5cf6")
    custom_css = Column(Text, nullable=True)

    # Domain
    custom_domain = Column(String(200), nullable=True)
    ssl_enabled = Column(Boolean, default=True)

    # Owner
    owner_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Subscription
    plan = Column(String(50), default="free")  # free, starter, professional, enterprise
    subscription_status = Column(String(20), default="active")
    subscription_start = Column(DateTime, nullable=True)
    subscription_end = Column(DateTime, nullable=True)

    # Usage limits
    max_products = Column(Integer, default=100)
    max_storage_mb = Column(Integer, default=1000)
    max_orders = Column(Integer, default=1000)
    max_vendors = Column(Integer, default=1)
    max_customers = Column(Integer, default=500)

    # Usage
    current_products = Column(Integer, default=0)
    current_storage_mb = Column(Float, default=0.0)
    current_orders = Column(Integer, default=0)
    current_customers = Column(Integer, default=0)

    # Billing
    billing_email = Column(String(255), nullable=True)
    stripe_customer_id = Column(String(200), nullable=True)
    billing_info = Column(JSON, default=dict)

    # Settings
    settings = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner_user = relationship("User", back_populates="tenant_profile")
    products = relationship("Product")
    users = relationship("TenantUser", back_populates="tenant")
    orders = relationship("Order")


class TenantUser(Base):
    __tablename__ = "tenant_users"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(50), default="member")  # owner, admin, manager, member
    permissions = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    tenant = relationship("Tenant", back_populates="users")
    user = relationship("User")


class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True)
    description = Column(Text, nullable=True)

    # Pricing
    monthly_price = Column(Float, default=0.0)
    yearly_price = Column(Float, default=0.0)
    currency = Column(String(10), default="USD")

    # Limits
    max_products = Column(Integer, default=100)
    max_storage_mb = Column(Integer, default=1000)
    max_orders = Column(Integer, default=1000)
    max_vendors = Column(Integer, default=1)
    max_customers = Column(Integer, default=500)

    # Features
    features = Column(JSON, default=list)  # ["custom_domain", "api_access", "analytics"]
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)

    stripe_price_monthly_id = Column(String(200), nullable=True)
    stripe_price_yearly_id = Column(String(200), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

