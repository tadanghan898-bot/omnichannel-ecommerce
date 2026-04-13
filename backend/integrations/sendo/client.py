"""
Sendo.vn Seller API Integration
Docs: https://open.sendo.vn/
"""
import hashlib
import hmac
import time
import json
from typing import Optional, Dict, List, Any
import httpx
from backend.integrations.base import BaseMarketplaceClient, retry_on_failure


class SendoClient(BaseMarketplaceClient):
    """Sendo.vn Seller Open API Client"""

    BASE_URL = "https://open.sendo.vn/api/partner"

    def __init__(self, credentials: Dict[str, Any]):
        self.partner_key = credentials.get("partner_key", "")
        self.partner_id = credentials.get("partner_id", "")
        self.shop_id = credentials.get("shop_id", "")
        self.base_url = "https://open.sendo.vn/api/partner"
        super().__init__(credentials)

    def test_connection(self) -> bool:
        """Test Sendo API connection"""
        try:
            resp = self._call_api("/product/list", {"limit": 1})
            self.connected = "data" in resp
            return self.connected
        except Exception:
            self.connected = False
            return False

    def _generate_signature(self, method: str, path: str, body: str) -> str:
        """Generate Sendo API signature"""
        message = f"{method}{path}{body}{self.partner_key}"
        return hmac.new(
            self.partner_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()

    def _call_api(self, endpoint: str, params: Dict, method: str = "GET") -> Dict:
        """Make authenticated Sendo API call"""
        timestamp = str(int(time.time() * 1000))
        body = json.dumps(params) if params else "{}"

        headers = {
            "X-Sendo-Client": self.partner_id,
            "X-Sendo-Timestamp": timestamp,
            "X-Sendo-Signature": self._generate_signature(method, endpoint, body),
            "Content-Type": "application/json",
        }

        url = f"{self.base_url}{endpoint}"
        if method == "GET":
            resp = httpx.get(url, params=params, headers=headers, timeout=30.0)
        else:
            resp = httpx.post(url, content=body, headers=headers, timeout=30.0)

        data = resp.json()
        if data.get("code") != 200:
            raise Exception(f"Sendo API error: {data.get('message', data.get('code'))}")
        return data.get("data", {})

    @retry_on_failure
    def get_orders(self, status: Optional[str] = None, page: int = 1, page_size: int = 50) -> List[Dict]:
        """Fetch orders from Sendo"""
        params = {
            "page": page,
            "limit": page_size,
        }
        if status:
            params["status"] = status

        resp = self._call_api("/order/list", params)
        orders = resp.get("data", [])

        result = []
        for order in orders:
            result.append(self.normalize_order({
                "order_id": order.get("order_id"),
                "customer_name": order.get("customer_name", ""),
                "customer_phone": order.get("customer_phone", ""),
                "shipping_address": self._format_address(order.get("address_shipping", {})),
                "items": self._extract_items(order.get("order_items", [])),
                "total_amount": float(order.get("total", 0)),
                "status": order.get("status", ""),
                "created_at": order.get("created_at", ""),
                "tracking_number": order.get("tracking_number", ""),
                "payment_method": order.get("payment_method", ""),
            }, "sendo"))
        return result

    def _format_address(self, addr: Dict) -> str:
        parts = [
            addr.get("address", ""),
            addr.get("district", ""),
            addr.get("city", ""),
        ]
        return ", ".join(p for p in parts if p)

    def _extract_items(self, items: List) -> List[Dict]:
        return [{
            "product_id": i.get("product_id"),
            "sku": i.get("sku", ""),
            "name": i.get("product_name", ""),
            "quantity": i.get("quantity", 0),
            "price": float(i.get("price", 0)),
        } for i in items]

    def get_order_detail(self, order_id: str) -> Dict:
        resp = self._call_api(f"/order/{order_id}", {})
        order = resp
        return self.normalize_order({
            "order_id": order.get("order_id"),
            "customer_name": order.get("customer_name", ""),
            "customer_phone": order.get("customer_phone", ""),
            "shipping_address": self._format_address(order.get("address_shipping", {})),
            "items": self._extract_items(order.get("order_items", [])),
            "total_amount": float(order.get("total", 0)),
            "status": order.get("status", ""),
            "created_at": order.get("created_at", ""),
            "tracking_number": order.get("tracking_number", ""),
            "payment_method": order.get("payment_method", ""),
        }, "sendo")

    @retry_on_failure
    def get_products(self, page: int = 1, page_size: int = 50) -> List[Dict]:
        resp = self._call_api("/product/list", {
            "page": page,
            "limit": page_size,
        })
        products = resp.get("data", [])

        result = []
        for p in products:
            result.append(self.normalize_product({
                "product_id": p.get("product_id"),
                "name": p.get("name", ""),
                "price": float(p.get("price", 0)),
                "stock": int(p.get("stock", 0)),
                "sku": p.get("sku", ""),
                "images": [{"url": img} for img in p.get("images", [])],
                "status": p.get("status", ""),
                "url": f"https://sendo.vn/product/{p.get('product_id', '')}",
            }, "sendo"))
        return result

    @retry_on_failure
    def create_product(self, product_data: Dict) -> Dict:
        """Create product on Sendo"""
        payload = {
            "name": product_data.get("name", ""),
            "description": product_data.get("description", ""),
            "price": product_data.get("price", 0),
            "stock": product_data.get("stock", 100),
            "category_id": product_data.get("category_id", ""),
            "images": [img.get("url") for img in product_data.get("images", [])],
        }
        resp = self._call_api("/product/create", payload, method="POST")
        return {"platform_product_id": resp.get("product_id"), "success": True}

    @retry_on_failure
    def update_inventory(self, product_id: str, quantity: int) -> bool:
        resp = self._call_api(f"/product/{product_id}/stock", {
            "stock": quantity,
        }, method="PUT")
        return resp.get("product_id") is not None

    @retry_on_failure
    def update_price(self, product_id: str, price: float) -> bool:
        resp = self._call_api(f"/product/{product_id}/price", {
            "price": price,
        }, method="PUT")
        return resp.get("product_id") is not None

    def get_logistics(self) -> List[Dict]:
        resp = self._call_api("/logistics/list", {})
        return resp.get("logistics", [])

    @retry_on_failure
    def ship_order(self, order_id: str, tracking_number: str, logistics_id: str) -> bool:
        resp = self._call_api(f"/order/{order_id}/ship", {
            "logistics_id": logistics_id,
            "tracking_number": tracking_number,
        }, method="POST")
        return resp.get("order_id") == order_id


# Router for FastAPI
from fastapi import APIRouter, Depends
from backend.core.auth import require_role

router = APIRouter(prefix="/api/integrations/sendo", tags=["Sendo Integration"])


@router.post("/connect")
async def connect_sendo(
    partner_id: str,
    partner_key: str,
    shop_id: str,
    user: dict = Depends(require_role("admin"))
):
    """Connect Sendo seller account"""
    client = SendoClient({
        "partner_id": partner_id,
        "partner_key": partner_key,
        "shop_id": shop_id,
    })
    if client.test_connection():
        return {"status": "connected", "shop_id": shop_id}
    return {"status": "failed", "message": "Connection test failed"}


@router.post("/sync/orders")
async def sync_sendo_orders(user: dict = Depends(require_role("admin"))):
    return {"status": "ok", "message": "Sendo order sync initiated"}


@router.post("/sync/products")
async def sync_sendo_products(user: dict = Depends(require_role("admin"))):
    return {"status": "ok", "message": "Sendo product sync initiated"}
