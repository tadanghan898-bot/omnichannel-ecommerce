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

    # Supabase Keys
    SUPABASE_URL: str = "https://peznevsvvmtdhafursvd.supabase.co"
    SUPABASE_ANON_KEY: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBlem5ldnN2dm10ZGhhZnVyc3ZkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzYwNTgyNjEsImV4cCI6MjA5MTYzNDI2MX0.H9Hfu80epDg3iijutxBg6ccmBRPl-ubKa84ZYkuAzl0"
    SUPABASE_SERVICE_ROLE_KEY: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBlem5ldnN2dm10ZGhhZnVyc3ZkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NjA1ODI2MSwiZXhwIjoyMDkxNjM0MjYxfQ.z_CplQrGTPqS9ct9yWgP3h2scyaSuKAtAwlwDjmMOw0"

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()

# Database URL override from environment
_database_url = os.getenv("DATABASE_URL", settings.DATABASE_URL)
# Support DB_PASS env var for Supabase (GitHub Actions / Vercel)
if not _database_url or _database_url == settings.DATABASE_URL:
    _db_pass = os.getenv("SUPABASE_DB_PASSWORD", "") or os.getenv("DB_PASS", "")
    if _db_pass:
        import urllib.parse
        _encoded = urllib.parse.quote(_db_pass, safe='')
        _database_url = f"postgresql://postgres:{_encoded}@db.peznevsvvmtdhafursvd.supabase.co:5432/postgres"

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
