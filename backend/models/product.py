"""Product, Category, Brand, and Inventory Models"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from backend.database import Base
import enum


class ProductStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    OUT_OF_STOCK = "out_of_stock"
    DELETED = "deleted"


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, index=True)
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    parent = relationship("Category", remote_side=[id], backref="subcategories")
    products = relationship("Product", back_populates="category")


class Brand(Base):
    __tablename__ = "brands"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, index=True)
    logo_url = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    website = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    products = relationship("Product", back_populates="brand")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(100), unique=True, index=True, nullable=True)
    name = Column(String(500), nullable=False)
    slug = Column(String(500), unique=True, index=True)
    description = Column(Text, nullable=True)
    short_description = Column(String(500), nullable=True)

    # Pricing
    price = Column(Float, nullable=False)
    compare_at_price = Column(Float, nullable=True)
    cost_price = Column(Float, nullable=True)  # for profit calculation
    currency = Column(String(10), default="VND")

    # Inventory
    stock_quantity = Column(Integer, default=0)
    low_stock_threshold = Column(Integer, default=5)
    track_inventory = Column(Boolean, default=True)

    # Media
    images = Column(JSON, default=list)  # [{"url": "...", "alt": "..."}]
    thumbnail_url = Column(String(500), nullable=True)
    video_url = Column(String(500), nullable=True)

    # Organization
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=True)  # multi_vendor
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)  # multi_tenant

    # Attributes
    weight = Column(Float, nullable=True)
    dimensions = Column(JSON, nullable=True)  # {"length": 10, "width": 5, "height": 3}
    tags = Column(JSON, default=list)  # ["electronics", "sale"]
    attributes = Column(JSON, default=dict)  # {"color": "red", "size": "M"}
    variants = Column(JSON, default=list)  # for product variants

    # SEO & AI
    meta_title = Column(String(200), nullable=True)
    meta_description = Column(Text, nullable=True)
    ai_description = Column(Text, nullable=True)  # AI-enhanced description

    # Status
    status = Column(String(20), default=ProductStatus.ACTIVE.value)
    is_featured = Column(Boolean, default=False)
    is_bestseller = Column(Boolean, default=False)
    rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)

    # Dropshipping
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    supplier_url = Column(String(500), nullable=True)
    sync_status = Column(String(20), default="manual")

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    category = relationship("Category", back_populates="products")
    brand = relationship("Brand", back_populates="products")
    vendor = relationship("Vendor", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")
    cart_items = relationship("CartItem", back_populates="product")
    wishlist_items = relationship("WishlistItem", back_populates="product")
    reviews = relationship("Review", back_populates="product")
    inventory_logs = relationship("InventoryLog", back_populates="product")


class InventoryLog(Base):
    __tablename__ = "inventory_logs"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    change_type = Column(String(50), nullable=False)  # sale, restock, adjustment, return
    quantity_change = Column(Integer, nullable=False)
    previous_quantity = Column(Integer, nullable=False)
    new_quantity = Column(Integer, nullable=False)
    reason = Column(String(200), nullable=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="inventory_logs")


class WishlistItem(Base):
    __tablename__ = "wishlist_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="wishlist")
    product = relationship("Product", back_populates="wishlist_items")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    rating = Column(Integer, nullable=False)  # 1-5
    title = Column(String(200), nullable=True)
    comment = Column(Text, nullable=True)
    images = Column(JSON, default=list)
    is_verified_purchase = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=True)
    helpful_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    product = relationship("Product", back_populates="reviews")
    user = relationship("User", back_populates="reviews")
