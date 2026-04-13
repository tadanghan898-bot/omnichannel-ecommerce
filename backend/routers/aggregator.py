"""
Unified Marketplace Orders Router
Aggregated view of all orders across connected platforms
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from backend.core.auth import require_role

router = APIRouter(prefix="/api/integrations/unified", tags=["Unified Marketplace"])


def _get_platform_credentials():
    """
    Load platform credentials from DB or config.
    In production, this would fetch from a credentials/secrets store.
    Returns dict: {platform_name: credentials_dict}
    """
    import os
    return {
        "shopee": {
            "partner_id": os.getenv("SHOPEE_PARTNER_ID", ""),
            "partner_key": os.getenv("SHOPEE_PARTNER_KEY", ""),
            "shop_id": os.getenv("SHOPEE_SHOP_ID", ""),
            "access_token": os.getenv("SHOPEE_ACCESS_TOKEN", ""),
        },
        "lazada": {
            "app_key": os.getenv("LAZADA_APP_KEY", ""),
            "app_secret": os.getenv("LAZADA_APP_SECRET", ""),
            "access_token": os.getenv("LAZADA_ACCESS_TOKEN", ""),
            "country": os.getenv("LAZADA_COUNTRY", "vn"),
        },
        "tiktok": {
            "app_key": os.getenv("TIKTOK_APP_KEY", ""),
            "app_secret": os.getenv("TIKTOK_APP_SECRET", ""),
            "access_token": os.getenv("TIKTOK_ACCESS_TOKEN", ""),
            "shop_id": os.getenv("TIKTOK_SHOP_ID", ""),
            "region": os.getenv("TIKTOK_REGION", "VN"),
        },
        "facebook": {
            "app_id": os.getenv("FACEBOOK_APP_ID", ""),
            "app_secret": os.getenv("FACEBOOK_APP_SECRET", ""),
            "access_token": os.getenv("FACEBOOK_ACCESS_TOKEN", ""),
            "page_id": os.getenv("FACEBOOK_PAGE_ID", ""),
            "catalog_id": os.getenv("FACEBOOK_CATALOG_ID", ""),
        },
        "sendo": {
            "partner_id": os.getenv("SENDO_PARTNER_ID", ""),
            "partner_key": os.getenv("SENDO_PARTNER_KEY", ""),
            "shop_id": os.getenv("SENDO_SHOP_ID", ""),
        },
    }


@router.get("/orders")
async def get_unified_orders(
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 50,
    user: dict = Depends(require_role("admin")),
):
    """
    Get aggregated orders from all connected marketplace platforms.
    Requires admin role.
    """
    credentials = _get_platform_credentials()
    active_platforms = {
        k: v for k, v in credentials.items()
        if any(v.values())
    }

    if not active_platforms:
        return {
            "orders": [],
            "total": 0,
            "platforms": [],
            "platform_counts": {},
            "errors": {"message": "No marketplace platforms configured. Set API credentials as environment variables."},
        }

    try:
        from backend.aggregator import OrderAggregator
        aggregator = OrderAggregator(active_platforms)
        return aggregator.get_all_orders(status=status, page=page, page_size=page_size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch orders: {str(e)}")


@router.post("/sync")
async def sync_all_platforms(
    user: dict = Depends(require_role("admin")),
):
    """Trigger sync on all connected platforms"""
    try:
        from backend.sync import get_scheduler
        scheduler = get_scheduler()
        if scheduler:
            scheduler.sync_now()
            return {"status": "ok", "message": "Sync triggered on all platforms"}
        return {"status": "ok", "message": "Scheduler not running - sync triggered manually"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


@router.get("/platforms/status")
async def get_platforms_status(
    user: dict = Depends(require_role("admin")),
):
    """Get connection status for all marketplace platforms"""
    credentials = _get_platform_credentials()
    from backend.aggregator import OrderAggregator
    aggregator = OrderAggregator(credentials)
    return aggregator.get_platform_summary()
