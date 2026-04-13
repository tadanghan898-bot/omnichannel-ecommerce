"""
ULTIMATE E-COMMERCE PLATFORM - Database Configuration
Supports SQLite (dev) and PostgreSQL (prod)
"""
import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
from sqlalchemy.pool import StaticPool
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./ecommerce.db"
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    PLATFORM_MODE: str = "ULTIMATE"  # BASIC, MARKETPLACE, SAAS, SOCIAL, AI_STORE, DROPSHIPPING, ULTIMATE

    # Payment API Keys (set in env)
    STRIPE_SECRET_KEY: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""
    PAYPAL_CLIENT_ID: str = ""
    PAYPAL_SECRET: str = ""

    # AI Settings
    OPENAI_API_KEY: str = ""

    # SMTP Settings
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()

# Database URL override from environment
_database_url = os.getenv("DATABASE_URL", settings.DATABASE_URL)

# Engine configuration
if _database_url.startswith("sqlite"):
    engine = create_engine(
        _database_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
elif "supabase" in _database_url.lower():
    # Supabase PostgreSQL with SSL
    engine = create_engine(
        _database_url,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        connect_args={"sslmode": "require"},
    )
else:
    engine = create_engine(
        _database_url,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database - import all models to register them with Base"""
    # Import all models to ensure they are registered
    from backend.models import (
        user, product, order, cart, payment,
        multi_vendor, multi_tenant, social, ai_engine, dropship
    )
    Base.metadata.create_all(bind=engine)
