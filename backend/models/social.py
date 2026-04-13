"""Social Commerce Models - Livestream, Posts, Community"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.database import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)

    type = Column(String(20), default="post")  # post, story, reel, livestream
    content = Column(Text, nullable=False)
    media = Column(JSON, default=list)  # [{"type": "image", "url": "..."}]
    product_ids = Column(JSON, default=list)  # tagged products

    # Engagement
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)

    # Status
    is_published = Column(Boolean, default=True)
    is_pinned = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)

    # Hashtags
    hashtags = Column(JSON, default=list)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    likes = relationship("PostLike", back_populates="post", cascade="all, delete-orphan")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)

    content = Column(Text, nullable=False)
    like_count = Column(Integer, default=0)
    is_approved = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    post = relationship("Post", back_populates="comments")
    replies = relationship("Comment", remote_side=[id], backref="parent")


class PostLike(Base):
    __tablename__ = "post_likes"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    post = relationship("Post", back_populates="likes")


class Livestream(Base):
    __tablename__ = "livestreams"

    id = Column(Integer, primary_key=True, index=True)
    host_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)

    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    thumbnail_url = Column(String(500), nullable=True)

    # Stream URL (for embedding)
    stream_url = Column(String(500), nullable=True)
    embed_url = Column(String(500), nullable=True)

    # Products being featured
    product_ids = Column(JSON, default=list)

    # Status
    status = Column(String(20), default="scheduled")  # scheduled, live, ended
    scheduled_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)

    # Engagement
    viewer_count = Column(Integer, default=0)
    peak_viewers = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)

    # Sales from livestream
    sales_count = Column(Integer, default=0)
    sales_amount = Column(Float, default=0.0)

    created_at = Column(DateTime, default=datetime.utcnow)


class Influencer(Base):
    __tablename__ = "influencers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)

    display_name = Column(String(200), nullable=True)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(500), nullable=True)

    # Social stats
    followers_count = Column(Integer, default=0)
    following_count = Column(Integer, default=0)
    post_count = Column(Integer, default=0)

    # Platform links
    social_links = Column(JSON, default=dict)  # {"facebook": "...", "instagram": "...", "tiktok": "..."}

    # Performance
    total_sales = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)
    commission_earned = Column(Float, default=0.0)

    # Status
    tier = Column(String(20), default="bronze")  # bronze, silver, gold, platinum
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class InfluencerCommission(Base):
    __tablename__ = "influencer_commissions"

    id = Column(Integer, primary_key=True, index=True)
    influencer_id = Column(Integer, ForeignKey("influencers.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)

    commission_rate = Column(Float, default=10.0)
    order_amount = Column(Float, nullable=False)
    commission_amount = Column(Float, nullable=False)

    status = Column(String(20), default="pending")  # pending, approved, paid
    paid_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
