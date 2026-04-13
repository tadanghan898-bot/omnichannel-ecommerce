"""
Shopee Seller API Integration
Docs: https://open.shopee.com/documents
"""
import hashlib
import hmac
import time
import urllib.parse
from typing import Optional, Dict, List, Any
import httpx
from backend.integrations.base import BaseMarketplaceClient, retry_on_failure


class ShopeeClient(BaseMarketplaceClient):
    """Shopee Seller API v2 Client"""

    BASE_URL = "https://partner.shopee.com/api/v2"

    def __init__(self, credentials: Dict[str, Any]):
        self.partner_id = credentials.get("partner_id", "")
        self.partner_key = credentials.get("partner_key", "")
        self.shop_id = credentials.get("shop_id", "")
        self.access_token = credentials.get("access_token", "")
        self.host = "partner.shopee.com"
        self.path = "/api/v2/shop/"  # default path
        super().__init__(credentials)

    def test_connection(self) -> bool:
        """Test Shopee API connection"""
        try:
            resp = self._call_api("/api/v2/shop/get_profile", {"shop_id": int(self.shop_id)})
            self.connected = resp.get("error") == 0
            return self.connected
        except Exception as e:
            logger.error(f"Shopee connection failed: {e}")
            self.connected = False
            return False

    def _generate_signature(self, path: str, params: Dict) -> str:
        """Generate Shopee API signature"""
        base_string = f"{self.host}{path}{self.partner_id}"
        for k, v in sorted(params.items()):
            base_string += f"{k}{v}"
        return hmac.new(
            self.partner_key.encode(),
            base_string.encode(),
            hashlib.sha256
        ).hexdigest()

    def _call_api(self, path: str, params: Dict, method: str = "POST") -> Dict:
        """Make authenticated Shopee API call"""
        timestamp = int(time.time())
        full_params = {
            "partner_id": int(self.partner_id),
            "shop_id": int(self.shop_id),
            "timestamp": timestamp,
            "access_token": self.access_token,
            **params
        }

        signature = self._generate_signature(path, full_params)
        full_params["sign"] = signature

        url = f"https://{self.host}{path}"
        if method == "GET":
            resp = self.client.get(url, params=full_params)
        else:
            resp = self.client.post(url, json=full_params)

        data = resp.json()
        if data.get("error"):
            raise Exception(f"Shopee API error: {data.get('message', data.get('error'))}")
        return data.get("response", {})

    @retry_on_failure
    def get_orders(self, status: Optional[str] = None, page: int = 1, page_size: int = 50) -> List[Dict]:
        """Fetch orders from Shopee"""
        # Map status to Shopee status codes
        status_map = {
            "pending": "unpaid",
            "confirmed": "ready_to_ship",
            "shipped": "shipped",
            "delivered": "completed",
            "cancelled": "cancelled",
        }
        order_status = status_map.get(status, "all") if status else "all"

        params = {
            "order_status": order_status,
            "page_size": page_size,
            "cursor": (page - 1) * page_size,
        }

        resp = self._call_api("/api/v2/order/get_orders", params)
        orders = resp.get("order_list", [])

        result = []
        for order in orders:
            result.append(self.normalize_order({
                "order_id": order.get("order_sn"),
                "customer_name": order.get("recipient_address", {}).get("name", ""),
                "customer_phone": order.get("recipient_address", {}).get("phone", ""),
                "shipping_address": self._format_address(order.get("recipient_address", {})),
                "items": self._extract_items(order.get("item_list", [])),
                "total_amount": order.get("total_amount", 0),
                "status": order.get("order_status"),
                "created_at": order.get("create_time"),
                "tracking_number": order.get("tracking_no", ""),
                "payment_method": order.get("payment_method", ""),
            }, "shopee"))
        return result

    def _format_address(self, addr: Dict) -> str:
        parts = [addr.get("address", ""), addr.get("district", ""),
                addr.get("city", ""), addr.get("region", "")]
        return ", ".join(p for p in parts if p)

    def _extract_items(self, items: List) -> List[Dict]:
        return [{
            "product_id": i.get("item_id"),
            "sku": i.get("item_sku", ""),
            "name": i.get("item_name", ""),
            "quantity": i.get("model_quantity_purchased", 0),
            "price": i.get("model_discounted_price", 0),
        } for i in items]

    def get_order_detail(self, order_id: str) -> Dict:
        resp = self._call_api("/api/v2/order/get_order_detail", {"order_sn": order_id})
        order = resp.get("order", {})
        return self.normalize_order({
            "order_id": order.get("order_sn"),
            "customer_name": order.get("recipient_address", {}).get("name", ""),
            "customer_phone": order.get("recipient_address", {}).get("phone", ""),
            "shipping_address": self._format_address(order.get("recipient_address", {})),
            "items": self._extract_items(order.get("items", [])),
            "total_amount": order.get("total_amount", 0),
            "status": order.get("status"),
            "created_at": order.get("create_time"),
            "tracking_number": order.get("tracking_no", ""),
            "payment_method": order.get("payment_method", ""),
        }, "shopee")

    @retry_on_failure
    def get_products(self, page: int = 1, page_size: int = 50) -> List[Dict]:
        resp = self._call_api("/api/v2/product/get_item_list", {
            "page_size": page_size,
            "offset": (page - 1) * page_size,
        })
        products = resp.get("item", [])

        result = []
        for p in products:
            result.append(self.normalize_product({
                "product_id": p.get("item_id"),
                "name": p.get("item_name", ""),
                "price": p.get("price_max", 0),
                "stock": p.get("stock_info", [{}])[0].get("stock", 0),
                "sku": p.get("item_sku", ""),
                "images": [{"url": img.get("url", "")} for img in p.get("images", [])],
                "status": p.get("status", ""),
                "url": f"https://shopee.vn/product/{self.shop_id}/{p.get('item_id', '')}",
            }, "shopee"))
        return result

    @retry_on_failure
    def create_product(self, product_data: Dict) -> Dict:
        """Create product on Shopee"""
        payload = {
            "item_name": product_data.get("name", ""),
            "description": product_data.get("description", ""),
            "price": product_data.get("price", 0),
            "stock": product_data.get("stock", 100),
            "category_id": product_data.get("category_id", 0),
            "images": [{"url": img} for img in product_data.get("images", [])],
        }
        resp = self._call_api("/api/v2/product/add_item", payload)
        return {"platform_product_id": resp.get("item_id"), "success": True}

    @retry_on_failure
    def update_inventory(self, product_id: str, quantity: int) -> bool:
        resp = self._call_api("/api/v2/product/update_stock", {
            "item_id": int(product_id),
            "stock_info": [{"stock": quantity}],
        })
        return resp.get("item_id") is not None

    @retry_on_failure
    def update_price(self, product_id: str, price: float) -> bool:
        resp = self._call_api("/api/v2/product/update_price", {
            "item_id": int(product_id),
            "price": price,
        })
        return resp.get("item_id") is not None

    def get_logistics(self) -> List[Dict]:
        resp = self._call_api("/api/v2/logistics/get_logistics", {})
        return resp.get("logistics", [])

    @retry_on_failure
    def ship_order(self, order_id: str, tracking_number: str, logistics_id: str) -> bool:
        resp = self._call_api("/api/v2/logistics/set_logistics", {
            "order_sn": order_id,
            "logistics_id": int(logistics_id),
            "tracking_number": tracking_number,
        })
        return resp.get("order_sn") == order_id

    @retry_on_failure
    def get_order_status(self, order_id: str) -> str:
        """Get current order status"""
        detail = self.get_order_detail(order_id)
        return detail.get("status", "")


# Router for FastAPI
from fastapi import APIRouter, Depends
from backend.core.auth import require_role

router = APIRouter(prefix="/api/integrations/shopee", tags=["Shopee Integration"])


@router.post("/connect")
async def connect_shopee(
    partner_id: str,
    partner_key: str,
    shop_id: str,
    access_token: str,
    user: dict = Depends(require_role("admin"))
):
    """Connect Shopee seller account"""
    client = ShopeeClient({
        "partner_id": partner_id,
        "partner_key": partner_key,
        "shop_id": shop_id,
        "access_token": access_token,
    })
    if client.test_connection():
        # Save credentials to DB
        return {"status": "connected", "shop_id": shop_id}
    return {"status": "failed", "message": "Connection test failed"}


@router.post("/sync/orders")
async def sync_shopee_orders(user: dict = Depends(require_role("admin"))):
    """Sync orders from Shopee"""
    # This would be called by the sync scheduler
    return {"status": "ok", "message": "Order sync initiated"}


@router.post("/sync/products")
async def sync_shopee_products(user: dict = Depends(require_role("admin"))):
    """Sync products from Shopee"""
    return {"status": "ok", "message": "Product sync initiated"}
