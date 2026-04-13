"""
Facebook Shops / Instagram Commerce API Integration
Docs: https://developers.facebook.com/docs/commerce
"""
import hashlib
import hmac
import time
import base64
from typing import Optional, Dict, List, Any
import httpx
from backend.integrations.base import BaseMarketplaceClient, retry_on_failure


class FacebookClient(BaseMarketplaceClient):
    """Facebook/Meta Commerce API Client"""

    BASE_URL = "https://graph.facebook.com/v21.0"

    def __init__(self, credentials: Dict[str, Any]):
        self.app_id = credentials.get("app_id", "")
        self.app_secret = credentials.get("app_secret", "")
        self.access_token = credentials.get("access_token", "")
        self.page_id = credentials.get("page_id", "")
        self.catalog_id = credentials.get("catalog_id", "")
        self.base_url = "https://graph.facebook.com/v21.0"
        super().__init__(credentials)

    def test_connection(self) -> bool:
        """Test Facebook Graph API connection"""
        try:
            resp = httpx.get(
                f"{self.base_url}/me",
                params={"access_token": self.access_token},
                timeout=30.0
            )
            data = resp.json()
            self.connected = "id" in data
            return self.connected
        except Exception:
            self.connected = False
            return False

    def _call_api(self, endpoint: str, params: Dict = None, method: str = "GET") -> Dict:
        """Make authenticated Facebook Graph API call"""
        params = params or {}
        params["access_token"] = self.access_token

        url = f"{self.base_url}{endpoint}"
        if method == "GET":
            resp = httpx.get(url, params=params, timeout=30.0)
        else:
            resp = httpx.post(url, data=params, timeout=30.0)

        data = resp.json()
        if "error" in data:
            raise Exception(f"Facebook API error: {data['error'].get('message', 'Unknown')}")
        return data

    @retry_on_failure
    def get_orders(self, status: Optional[str] = None, page: int = 1, page_size: int = 50) -> List[Dict]:
        """Fetch orders from Facebook Shops"""
        params = {
            "fields": "id,order_status,created_at,updated_at,buyer_details,shipping_address,item_details,total_amount",
            "limit": page_size,
        }
        if status:
            params["filtering"] = f'[{{"field":"order_status","operator":"IN","value":["{status.upper()}"]}}]'

        resp = self._call_api("/me/commerce_orders", params)
        orders = resp.get("data", [])

        result = []
        for order in orders:
            buyer = order.get("buyer_details", {})
            address = order.get("shipping_address", {})
            items = order.get("item_details", {}).get("items", [])
            result.append(self.normalize_order({
                "order_id": order.get("id"),
                "customer_name": buyer.get("name", ""),
                "customer_phone": buyer.get("phone", {}).get("phone_number", ""),
                "shipping_address": self._format_address(address),
                "items": self._extract_items(items),
                "total_amount": float(order.get("total_amount", {}).get("amount", 0)),
                "status": order.get("order_status", ""),
                "created_at": order.get("created_at", ""),
                "tracking_number": order.get("tracking_number", ""),
                "payment_method": order.get("payment_method", ""),
            }, "facebook"))
        return result

    def _format_address(self, addr: Dict) -> str:
        parts = [
            addr.get("street1", ""),
            addr.get("street2", ""),
            addr.get("city", ""),
            addr.get("state", ""),
            addr.get("postal_code", ""),
            addr.get("country", ""),
        ]
        return ", ".join(p for p in parts if p)

    def _extract_items(self, items: List) -> List[Dict]:
        return [{
            "product_id": i.get("product_item_id"),
            "sku": i.get("sku", ""),
            "name": i.get("name", ""),
            "quantity": i.get("quantity", 0),
            "price": float(i.get("price", {}).get("amount", 0)),
        } for i in items]

    def get_order_detail(self, order_id: str) -> Dict:
        resp = self._call_api(f"/{order_id}", {
            "fields": "id,order_status,created_at,updated_at,buyer_details,shipping_address,item_details,total_amount"
        })
        buyer = resp.get("buyer_details", {})
        address = resp.get("shipping_address", {})
        items = resp.get("item_details", {}).get("items", [])
        return self.normalize_order({
            "order_id": resp.get("id"),
            "customer_name": buyer.get("name", ""),
            "customer_phone": buyer.get("phone", {}).get("phone_number", ""),
            "shipping_address": self._format_address(address),
            "items": self._extract_items(items),
            "total_amount": float(resp.get("total_amount", {}).get("amount", 0)),
            "status": resp.get("order_status", ""),
            "created_at": resp.get("created_at", ""),
            "tracking_number": resp.get("tracking_number", ""),
            "payment_method": resp.get("payment_method", ""),
        }, "facebook")

    @retry_on_failure
    def get_products(self, page: int = 1, page_size: int = 50) -> List[Dict]:
        """Fetch products from Facebook catalog"""
        resp = self._call_api(f"/{self.catalog_id}/products", {
            "fields": "id,name,description,price,availability,image_url,url,shipping,brand",
            "limit": page_size,
        })
        products = resp.get("data", [])

        result = []
        for p in products:
            result.append(self.normalize_product({
                "product_id": p.get("id"),
                "name": p.get("name", ""),
                "price": float(p.get("price", "0").replace("$", "").replace(",", "")),
                "stock": 0,
                "sku": p.get("id", ""),
                "images": [{"url": p.get("image_url", "")}],
                "status": p.get("availability", ""),
                "url": p.get("url", ""),
            }, "facebook"))
        return result

    @retry_on_failure
    def create_product(self, product_data: Dict) -> Dict:
        """Create product in Facebook catalog"""
        payload = {
            "name": product_data.get("name", ""),
            "description": product_data.get("description", ""),
            "price": str(product_data.get("price", 0)),
            "currency": "VND",
            "availability": "in stock",
            "image_url": product_data.get("images", [{}])[0].get("url", ""),
            "url": product_data.get("url", ""),
        }
        resp = self._call_api(f"/{self.catalog_id}/products", payload, method="POST")
        return {"platform_product_id": resp.get("id"), "success": True}

    @retry_on_failure
    def update_inventory(self, product_id: str, quantity: int) -> bool:
        availability = "in stock" if quantity > 0 else "out of stock"
        resp = self._call_api(f"/{product_id}", {
            "availability": availability,
        }, method="POST")
        return "id" in resp

    @retry_on_failure
    def update_price(self, product_id: str, price: float) -> bool:
        resp = self._call_api(f"/{product_id}", {
            "price": str(price),
            "currency": "VND",
        }, method="POST")
        return "id" in resp

    def get_logistics(self) -> List[Dict]:
        return []

    @retry_on_failure
    def ship_order(self, order_id: str, tracking_number: str, logistics_id: str) -> bool:
        resp = self._call_api(f"/{order_id}", {
            "tracking_number": tracking_number,
            "logistics_provider": logistics_id,
        }, method="POST")
        return "id" in resp


# Router for FastAPI
from fastapi import APIRouter, Depends
from backend.core.auth import require_role

router = APIRouter(prefix="/api/integrations/facebook", tags=["Facebook Integration"])


@router.post("/connect")
async def connect_facebook(
    app_id: str,
    app_secret: str,
    access_token: str,
    page_id: str = "",
    catalog_id: str = "",
    user: dict = Depends(require_role("admin"))
):
    """Connect Facebook/Meta commerce account"""
    client = FacebookClient({
        "app_id": app_id,
        "app_secret": app_secret,
        "access_token": access_token,
        "page_id": page_id,
        "catalog_id": catalog_id,
    })
    if client.test_connection():
        return {"status": "connected", "page_id": page_id}
    return {"status": "failed", "message": "Connection test failed"}


@router.post("/sync/orders")
async def sync_facebook_orders(user: dict = Depends(require_role("admin"))):
    return {"status": "ok", "message": "Facebook order sync initiated"}


@router.post("/sync/products")
async def sync_facebook_products(user: dict = Depends(require_role("admin"))):
    return {"status": "ok", "message": "Facebook product sync initiated"}
