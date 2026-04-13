"""
TikTok Shop Seller API Integration
Docs: https://partner.tiktokshop.com/doc
"""
import hashlib
import hmac
import time
import json
import urllib.parse
from typing import Optional, Dict, List, Any
import httpx
from backend.integrations.base import BaseMarketplaceClient, retry_on_failure


class TikTokClient(BaseMarketplaceClient):
    """TikTok Shop Open Platform API v2 Client"""

    BASE_URL = "https://open.tiktokglobalshop.com"

    def __init__(self, credentials: Dict[str, Any]):
        self.app_key = credentials.get("app_key", "")
        self.app_secret = credentials.get("app_secret", "")
        self.access_token = credentials.get("access_token", "")
        self.shop_id = credentials.get("shop_id", "")
        self.region = credentials.get("region", "VN")
        self.base_url = f"https://open.tiktokglobalshop.com"
        self._token_expires_at = 0
        super().__init__(credentials)

    def test_connection(self) -> bool:
        """Test TikTok Shop API connection"""
        try:
            resp = self._call_api("/api/v2/shop/get_authorized_shop_info", {})
            self.connected = resp.get("data", {}).get("shop_list") is not None
            return self.connected
        except Exception as e:
            self.connected = False
            return False

    def _generate_signature(self, params: Dict) -> str:
        """Generate TikTok API signature"""
        sorted_items = sorted(params.items())
        message = "".join(f"{k}{v}" for k, v in sorted_items)
        return hashlib.sha256((self.app_secret + message + self.app_secret).encode()).hexdigest().upper()

    def _call_api(self, endpoint: str, params: Dict, method: str = "POST") -> Dict:
        """Make authenticated TikTok API call"""
        timestamp = str(int(time.time()))
        full_params = {
            "app_key": self.app_key,
            "timestamp": timestamp,
            "access_token": self.access_token,
            "shop_id": self.shop_id,
            **params
        }
        full_params["sign"] = self._generate_signature(full_params)

        url = f"{self.base_url}{endpoint}"
        if method == "GET":
            resp = httpx.get(url, params=full_params, timeout=30.0)
        else:
            resp = httpx.post(url, data=full_params, timeout=30.0)

        data = resp.json()
        if data.get("code", 0) != 0:
            raise Exception(f"TikTok API error: {data.get('message', data.get('code'))}")
        return data.get("data", {})

    @retry_on_failure
    def get_orders(self, status: Optional[str] = None, page: int = 1, page_size: int = 50) -> List[Dict]:
        """Fetch orders from TikTok Shop"""
        # Map status to TikTok status
        status_map = {
            "pending": "WAITING_PAYMENT",
            "confirmed": "WAITING_SELLER_PROCESS",
            "shipped": "IN_TRANSIT",
            "delivered": "COMPLETED",
            "cancelled": "CANCELLED",
        }
        order_status = status_map.get(status, "") if status else ""

        params = {
            "order_status": order_status,
            "page_size": page_size,
            "max_order_date": int(time.time()),
            "min_order_date": int(time.time()) - 86400 * 90,
        }

        resp = self._call_api("/api/v2/order/get_order_list", params)
        orders = resp.get("order_list", [])

        result = []
        for order in orders:
            result.append(self.normalize_order({
                "order_id": order.get("order_id"),
                "customer_name": order.get("recipient_address", {}).get("full_name", ""),
                "customer_phone": order.get("recipient_address", {}).get("phone_number", ""),
                "shipping_address": self._format_address(order.get("recipient_address", {})),
                "items": self._extract_items(order.get("line_items", [])),
                "total_amount": float(order.get("total_amount", 0)),
                "status": order.get("order_status"),
                "created_at": order.get("create_time"),
                "tracking_number": order.get("tracking_number", ""),
                "payment_method": order.get("payment_method", ""),
            }, "tiktok"))
        return result

    def _format_address(self, addr: Dict) -> str:
        parts = [
            addr.get("full_address", ""),
            addr.get("district", ""),
            addr.get("city", ""),
            addr.get("region", ""),
        ]
        return ", ".join(p for p in parts if p)

    def _extract_items(self, items: List) -> List[Dict]:
        return [{
            "product_id": i.get("sku_id"),
            "sku": i.get("sku_code", ""),
            "name": i.get("product_name", ""),
            "quantity": i.get("quantity", 0),
            "price": float(i.get("unit_price", 0)),
        } for i in items]

    def get_order_detail(self, order_id: str) -> Dict:
        resp = self._call_api("/api/v2/order/get_order_detail", {"order_id": order_id})
        order = resp.get("order_detail", {})
        return self.normalize_order({
            "order_id": order.get("order_id"),
            "customer_name": order.get("recipient_address", {}).get("full_name", ""),
            "customer_phone": order.get("recipient_address", {}).get("phone_number", ""),
            "shipping_address": self._format_address(order.get("recipient_address", {})),
            "items": self._extract_items(order.get("line_items", [])),
            "total_amount": float(order.get("total_amount", 0)),
            "status": order.get("order_status"),
            "created_at": order.get("create_time"),
            "tracking_number": order.get("tracking_number", ""),
            "payment_method": order.get("payment_method", ""),
        }, "tiktok")

    @retry_on_failure
    def get_products(self, page: int = 1, page_size: int = 50) -> List[Dict]:
        resp = self._call_api("/api/v2/product/get_product_list", {
            "page_size": page_size,
            "cursor": (page - 1) * page_size,
        })
        products = resp.get("products", [])

        result = []
        for p in products:
            result.append(self.normalize_product({
                "product_id": p.get("product_id"),
                "name": p.get("product_name", ""),
                "price": float(p.get("skus", [{}])[0].get("price", 0)),
                "stock": int(p.get("skus", [{}])[0].get("stock_infos", [{}])[0].get("available_stock", 0)),
                "sku": p.get("skus", [{}])[0].get("sku_code", ""),
                "images": [{"url": img} for img in p.get("images", [])],
                "status": p.get("status", ""),
                "url": f"https://tiktok.shop/product/{p.get('product_id', '')}",
            }, "tiktok"))
        return result

    @retry_on_failure
    def create_product(self, product_data: Dict) -> Dict:
        """Create product on TikTok Shop"""
        payload = {
            "product_name": product_data.get("name", ""),
            "description": product_data.get("description", ""),
            "category_id": product_data.get("category_id", ""),
            "sku_list": [{
                "sku_code": product_data.get("sku", ""),
                "price": product_data.get("price", 0),
                "stock": product_data.get("stock", 100),
                "currency": "VND",
            }]
        }
        resp = self._call_api("/api/v2/product/create_product", payload)
        return {"platform_product_id": resp.get("product_id"), "success": True}

    @retry_on_failure
    def update_inventory(self, product_id: str, quantity: int) -> bool:
        resp = self._call_api("/api/v2/product/update_stock", {
            "product_id": product_id,
            "sku_stock_infos": [{"sku_id": product_id, "stock": quantity}],
        })
        return resp.get("product_id") is not None

    @retry_on_failure
    def update_price(self, product_id: str, price: float) -> bool:
        resp = self._call_api("/api/v2/product/update_price", {
            "product_id": product_id,
            "sku_price_infos": [{"sku_id": product_id, "price": price}],
        })
        return resp.get("product_id") is not None

    def get_logistics(self) -> List[Dict]:
        resp = self._call_api("/api/v2/logistics/get_logistics_info", {})
        return resp.get("logistics", [])

    @retry_on_failure
    def ship_order(self, order_id: str, tracking_number: str, logistics_id: str) -> bool:
        resp = self._call_api("/api/v2/order/ship_order", {
            "order_id": order_id,
            "logistics_id": logistics_id,
            "tracking_number": tracking_number,
        })
        return resp.get("order_id") == order_id

    @retry_on_failure
    def get_order_status(self, order_id: str) -> str:
        """Get current order status"""
        detail = self.get_order_detail(order_id)
        return detail.get("status", "")


# Router for FastAPI
from fastapi import APIRouter, Depends
from backend.core.auth import require_role

router = APIRouter(prefix="/api/integrations/tiktok", tags=["TikTok Shop Integration"])


@router.post("/connect")
async def connect_tiktok(
    app_key: str,
    app_secret: str,
    access_token: str,
    shop_id: str,
    region: str = "VN",
    user: dict = Depends(require_role("admin"))
):
    """Connect TikTok Shop seller account"""
    client = TikTokClient({
        "app_key": app_key,
        "app_secret": app_secret,
        "access_token": access_token,
        "shop_id": shop_id,
        "region": region,
    })
    if client.test_connection():
        return {"status": "connected", "shop_id": shop_id}
    return {"status": "failed", "message": "Connection test failed"}


@router.post("/sync/orders")
async def sync_tiktok_orders(user: dict = Depends(require_role("admin"))):
    return {"status": "ok", "message": "TikTok order sync initiated"}


@router.post("/sync/products")
async def sync_tiktok_products(user: dict = Depends(require_role("admin"))):
    return {"status": "ok", "message": "TikTok product sync initiated"}
