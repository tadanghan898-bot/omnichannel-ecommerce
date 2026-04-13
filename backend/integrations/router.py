"""
Unified Marketplace Integration Router
Registers all marketplace client routers under a single prefix
"""
from fastapi import APIRouter
from backend.core.auth import require_role

# Import all marketplace routers
try:
    from backend.integrations.shopee import router as shopee_router
except ImportError:
    shopee_router = None

try:
    from backend.integrations.lazada import router as lazada_router
except ImportError:
    lazada_router = None

try:
    from backend.integrations.tiktok import router as tiktok_router
except ImportError:
    tiktok_router = None

try:
    from backend.integrations.facebook import router as facebook_router
except ImportError:
    facebook_router = None

try:
    from backend.integrations.sendo import router as sendo_router
except ImportError:
    sendo_router = None


def register_integration_routes(app):
    """Register all marketplace integration routes with the FastAPI app"""
    integrations_router = APIRouter(prefix="/api/integrations", tags=["Marketplace Integrations"])

    if shopee_router:
        integrations_router.include_router(shopee_router)
    if lazada_router:
        integrations_router.include_router(lazada_router)
    if tiktok_router:
        integrations_router.include_router(tiktok_router)
    if facebook_router:
        integrations_router.include_router(facebook_router)
    if sendo_router:
        integrations_router.include_router(sendo_router)

    app.include_router(integrations_router)
