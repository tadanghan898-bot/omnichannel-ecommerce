"""AI Engine Models - Recommendations, Chatbot, Image Gen"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.database import Base


class AISession(Base):
    __tablename__ = "ai_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    session_type = Column(String(30), default="chatbot")  # chatbot, recommendation, image_gen
    session_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="ai_sessions")
    messages = relationship("AIMessage", back_populates="session", cascade="all, delete-orphan")


class AIMessage(Base):
    __tablename__ = "ai_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("ai_sessions.id"), nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    message_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("AISession", back_populates="messages")


class ProductRecommendation(Base):
    __tablename__ = "product_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    session_id = Column(Integer, ForeignKey("ai_sessions.id"), nullable=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    recommendation_type = Column(String(30), default="personalized")  # personalized, trending, similar, frequently_bought_together, new_arrivals
    score = Column(Float, default=0.0)
    reason = Column(String(200), nullable=True)  # "Because you viewed X", "Trending now"
    context = Column(JSON, default=dict)
    is_clicked = Column(Boolean, default=False)
    is_purchased = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class AIGeneratedImage(Base):
    __tablename__ = "ai_generated_images"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)

    prompt = Column(Text, nullable=False)
    negative_prompt = Column(Text, nullable=True)
    style = Column(String(100), nullable=True)  # realistic, cartoon, anime, etc.
    size = Column(String(20), default="1024x1024")

    # Output
    image_url = Column(String(500), nullable=True)
    seed = Column(Integer, nullable=True)
    steps = Column(Integer, default=30)
    cfg_scale = Column(Float, default=7.5)

    # Model used
    model_name = Column(String(100), nullable=True)

    # Status
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)

    credits_used = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


class SearchQuery(Base):
    __tablename__ = "search_queries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    query = Column(String(500), nullable=False)
    results_count = Column(Integer, default=0)
    clicked_product_ids = Column(JSON, default=list)
    converted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
