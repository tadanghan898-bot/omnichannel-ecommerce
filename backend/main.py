"""
ULTIMATE E-COMMERCE PLATFORM - Main Application
Modular FastAPI app with plugin-based module loading
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
try:
    from slowapi.errors import rate_limit_exceeded_handler
    from slowapi.middleware import SlowAPIMiddleware
except ImportError:
    rate_limit_exceeded_handler = None
    SlowAPIMiddleware = None

from backend.database import init_db, settings
from backend.core.config import get_platform_info

# Routers
from backend.routers.auth import router as auth_router
from backend.routers.products import router as products_router
from backend.routers.orders import router as orders_router
from backend.routers.cart import router as cart_router
from backend.routers.admin import router as admin_router
from backend.routers.vendors import router as vendors_router
from backend.routers.ai import router as ai_router
from backend.routers.dropship import router as dropship_router
from backend.routers.social import router as social_router
from backend.routers.tenants import router as tenants_router


# Platform info
PLATFORM = get_platform_info()

# Limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title="ULTIMATE E-COMMERCE PLATFORM",
    description=f"Modular e-commerce platform - Mode: {PLATFORM.get('mode', 'ULTIMATE')}. {PLATFORM.get('description', '')}",
    version="1.0.0",
    docs_url="/docs" if os.getenv("ENV") != "production" else None,
    redoc_url="/redoc" if os.getenv("ENV") != "production" else None,
)

# Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
if SlowAPIMiddleware:
    app.add_middleware(SlowAPIMiddleware)

# Rate limiter
app.state.limiter = limiter
if rate_limit_exceeded_handler:
    from fastapi import Request
    from fastapi.responses import JSONResponse
    @app.exception_handler(Exception)
    async def rate_handler(request: Request, exc: Exception):
        return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})


# Startup
@app.on_event("startup")
async def startup_event():
    init_db()
    print(f"\n{'='*60}")
    print(f"ULTIMATE E-COMMERCE PLATFORM")
    print(f"Mode: {PLATFORM.get('mode', 'ULTIMATE')}")
    print(f"Active Modules: {', '.join(PLATFORM.get('active_features', []))}")
    print(f"{'='*60}\n")


# Health check
@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "platform": PLATFORM.get("mode", "ULTIMATE"),
        "modules": PLATFORM.get("active_features", []),
    }


@app.get("/api/platform")
async def platform_info():
    return PLATFORM


# Register routers
app.include_router(auth_router)
app.include_router(products_router)
app.include_router(orders_router)
app.include_router(cart_router)
app.include_router(admin_router)

# Feature module routers (conditionally available)
if PLATFORM.get("multi_vendor"):
    app.include_router(vendors_router)
    print("[MODULE] Multi-vendor marketplace enabled")

if PLATFORM.get("multi_tenant"):
    app.include_router(tenants_router)
    print("[MODULE] Multi-tenant SaaS enabled")

if PLATFORM.get("social"):
    app.include_router(social_router)
    print("[MODULE] Social commerce enabled")

if PLATFORM.get("ai_engine"):
    app.include_router(ai_router)
    print("[MODULE] AI engine enabled")

if PLATFORM.get("dropship"):
    app.include_router(dropship_router)
    print("[MODULE] Dropshipping enabled")

# SEO router (always available)
try:
    from backend.seo.router import router as seo_router
    app.include_router(seo_router)
    print("[MODULE] SEO module enabled")
except ImportError:
    pass

# Marketplace integrations (always available)
try:
    from backend.integrations.router import register_integration_routes
    register_integration_routes(app)
    print("[MODULE] Marketplace integrations enabled (Shopee, Lazada, TikTok, Facebook, Sendo)")
except ImportError as e:
    print(f"[MODULE] Marketplace integrations not available: {e}")

# Unified marketplace aggregator
try:
    from backend.routers.aggregator import router as aggregator_router
    app.include_router(aggregator_router)
    print("[MODULE] Unified marketplace aggregator enabled")
except ImportError:
    pass


# Run with: uvicorn backend.main:app --reload
