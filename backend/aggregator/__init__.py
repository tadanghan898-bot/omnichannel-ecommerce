"""
OMNICHANNEL ORDER & PRODUCT AGGREGATOR
Unified view of orders/products across all marketplace platforms
"""
import logging
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
import asyncio

logger = logging.getLogger(__name__)

# Lazy import to avoid circular deps - clients loaded on demand
_clients: Dict[str, Any] = {}


def _get_client(platform: str, credentials: Dict):
    """Get or create marketplace client instance"""
    key = f"{platform}_{id(credentials)}"
    if key not in _clients:
        if platform == "shopee":
            from backend.integrations.shopee import ShopeeClient
            _clients[key] = ShopeeClient(credentials)
        elif platform == "lazada":
            from backend.integrations.lazada import LazadaClient
            _clients[key] = LazadaClient(credentials)
        elif platform == "tiktok":
            from backend.integrations.tiktok import TikTokClient
            _clients[key] = TikTokClient(credentials)
        elif platform == "facebook":
            from backend.integrations.facebook import FacebookClient
            _clients[key] = FacebookClient(credentials)
        elif platform == "sendo":
            from backend.integrations.sendo import SendoClient
            _clients[key] = SendoClient(credentials)
    return _clients[key]


class OrderAggregator:
    """Aggregate and normalize orders from all marketplace platforms"""

    def __init__(self, platform_credentials: Dict[str, Dict]):
        """
        Args:
            platform_credentials: Dict mapping platform name to credentials dict
            e.g. {"shopee": {...}, "lazada": {...}}
        """
        self.platform_credentials = platform_credentials
        self.platforms = list(platform_credentials.keys())

    def get_all_orders(
        self,
        status: Optional[str] = None,
        since_hours: int = 24,
        page: int = 1,
        page_size: int = 50,
    ) -> List[Dict]:
        """Fetch orders from all connected platforms, merged and sorted by date"""
        all_orders = []
        errors = {}

        for platform in self.platforms:
            try:
                creds = self.platform_credentials[platform]
                client = _get_client(platform, creds)
                orders = client.get_orders(status=status, page=page, page_size=page_size)
                for order in orders:
                    order["platform"] = platform
                all_orders.extend(orders)
            except Exception as e:
                logger.error(f"Failed to fetch orders from {platform}: {e}")
                errors[platform] = str(e)

        # Sort by created_at descending
        all_orders.sort(
            key=lambda x: x.get("created_at", ""),
            reverse=True
        )

        return {
            "orders": all_orders,
            "total": len(all_orders),
            "platforms": self.platforms,
            "platform_counts": {p: sum(1 for o in all_orders if o.get("platform") == p) for p in self.platforms},
            "errors": errors,
        }

    def get_platform_summary(self) -> Dict[str, Dict]:
        """Get summary stats for each platform"""
        summary = {}
        for platform in self.platforms:
            try:
                creds = self.platform_credentials[platform]
                client = _get_client(platform, creds)
                summary[platform] = {
                    "connected": client.connected,
                    "status": "active" if client.connected else "disconnected",
                }
            except Exception as e:
                summary[platform] = {"connected": False, "status": "error", "error": str(e)}
        return summary

    def sync_order_status(self, platform: str, order_id: str) -> Dict:
        """Get unified status for a specific order across platforms"""
        try:
            creds = self.platform_credentials.get(platform)
            if not creds:
                return {"error": f"Platform {platform} not configured"}
            client = _get_client(platform, creds)
            status = client.get_order_status(order_id)
            return {"platform": platform, "order_id": order_id, "status": status}
        except Exception as e:
            return {"platform": platform, "order_id": order_id, "error": str(e)}


class ProductAggregator:
    """Aggregate and manage products across all marketplace platforms"""

    def __init__(self, platform_credentials: Dict[str, Dict]):
        self.platform_credentials = platform_credentials
        self.platforms = list(platform_credentials.keys())

    def get_all_products(
        self,
        page: int = 1,
        page_size: int = 50,
    ) -> Dict[str, List[Dict]]:
        """Fetch products from all connected platforms"""
        all_products = {}
        errors = {}

        for platform in self.platforms:
            try:
                creds = self.platform_credentials[platform]
                client = _get_client(platform, creds)
                products = client.get_products(page=page, page_size=page_size)
                all_products[platform] = products
            except Exception as e:
                logger.error(f"Failed to fetch products from {platform}: {e}")
                errors[platform] = str(e)
                all_products[platform] = []

        return {
            "products": all_products,
            "platforms": self.platforms,
            "platform_counts": {p: len(all_products.get(p, [])) for p in self.platforms},
            "total_count": sum(len(v) for v in all_products.values()),
            "errors": errors,
        }

    def update_price_all_platforms(
        self,
        sku: str,
        price: float,
        product_id_map: Dict[str, str],
    ) -> Dict[str, bool]:
        """Update price on all platforms for a given product SKU"""
        results = {}
        for platform, product_id in product_id_map.items():
            try:
                creds = self.platform_credentials.get(platform)
                if not creds:
                    results[platform] = False
                    continue
                client = _get_client(platform, creds)
                results[platform] = client.update_price(product_id, price)
            except Exception as e:
                logger.error(f"Failed to update price on {platform}: {e}")
                results[platform] = False
        return results

    def update_stock_all_platforms(
        self,
        sku: str,
        quantity: int,
        product_id_map: Dict[str, str],
    ) -> Dict[str, bool]:
        """Update inventory on all platforms for a given product SKU"""
        results = {}
        for platform, product_id in product_id_map.items():
            try:
                creds = self.platform_credentials.get(platform)
                if not creds:
                    results[platform] = False
                    continue
                client = _get_client(platform, creds)
                results[platform] = client.update_inventory(product_id, quantity)
            except Exception as e:
                logger.error(f"Failed to update stock on {platform}: {e}")
                results[platform] = False
        return results


# Global aggregator instance (loaded from DB credentials in production)
_global_order_aggregator: Optional[OrderAggregator] = None
_global_product_aggregator: Optional[ProductAggregator] = None


def init_aggregators(platform_credentials: Dict[str, Dict]):
    global _global_order_aggregator, _global_product_aggregator
    _global_order_aggregator = OrderAggregator(platform_credentials)
    _global_product_aggregator = ProductAggregator(platform_credentials)


def get_order_aggregator() -> Optional[OrderAggregator]:
    return _global_order_aggregator


def get_product_aggregator() -> Optional[ProductAggregator]:
    return _global_product_aggregator
