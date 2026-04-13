"""
OMNICHANNEL E-COMMERCE - Base Integration Class
All marketplace clients inherit from this base class
"""
import httpx
import hashlib
import hmac
import time
import logging
from typing import Optional, Dict, List, Any
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseMarketplaceClient(ABC):
    """Base class for all marketplace API clients"""

    BASE_URL: str = ""

    def __init__(self, credentials: Dict[str, Any]):
        self.credentials = credentials
        self.client = httpx.Client(timeout=30.0)
        self.connected = False
        self.test_connection()

    @abstractmethod
    def test_connection(self) -> bool:
        """Test API connection with given credentials"""
        pass

    @abstractmethod
    def get_orders(self, status: Optional[str] = None, page: int = 1, page_size: int = 50) -> List[Dict]:
        """Fetch orders from marketplace"""
        pass

    @abstractmethod
    def get_order_detail(self, order_id: str) -> Dict:
        """Get detailed order information"""
        pass

    @abstractmethod
    def get_products(self, page: int = 1, page_size: int = 50) -> List[Dict]:
        """Fetch products from marketplace"""
        pass

    @abstractmethod
    def create_product(self, product_data: Dict) -> Dict:
        """Create/Update product on marketplace"""
        pass

    @abstractmethod
    def update_inventory(self, product_id: str, quantity: int) -> bool:
        """Update product inventory"""
        pass

    @abstractmethod
    def update_price(self, product_id: str, price: float) -> bool:
        """Update product price"""
        pass

    @abstractmethod
    def get_logistics(self) -> List[Dict]:
        """Get available shipping methods"""
        pass

    @abstractmethod
    def ship_order(self, order_id: str, tracking_number: str, logistics_id: str) -> bool:
        """Mark order as shipped with tracking info"""
        pass

    def close(self):
        self.client.close()

    @staticmethod
    def normalize_order(order: Dict, platform: str) -> Dict:
        """Convert marketplace order format to unified format"""
        return {
            "platform": platform,
            "platform_order_id": order.get("order_id", ""),
            "customer_name": order.get("customer_name", ""),
            "customer_phone": order.get("customer_phone", ""),
            "shipping_address": order.get("shipping_address", ""),
            "items": order.get("items", []),
            "total_amount": float(order.get("total_amount", 0)),
            "status": order.get("status", ""),
            "created_at": order.get("created_at", ""),
            "tracking_number": order.get("tracking_number", ""),
            "payment_method": order.get("payment_method", ""),
        }

    @staticmethod
    def normalize_product(product: Dict, platform: str) -> Dict:
        """Convert marketplace product format to unified format"""
        return {
            "platform": platform,
            "platform_product_id": product.get("product_id", ""),
            "name": product.get("name", ""),
            "price": float(product.get("price", 0)),
            "stock": int(product.get("stock", 0)),
            "sku": product.get("sku", ""),
            "images": product.get("images", []),
            "status": product.get("status", ""),
            "url": product.get("url", ""),
        }


def generate_signature(params: Dict, secret: str) -> str:
    """Generate HMAC-SHA256 signature for API calls"""
    sorted_params = sorted(params.items())
    message = "&".join(f"{k}={v}" for k, v in sorted_params)
    return hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()


def retry_on_failure(func, max_retries=3, delay=1):
    """Decorator to retry failed API calls"""
    def wrapper(*args, **kwargs):
        for i in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if i == max_retries - 1:
                    raise
                logger.warning(f"Retry {i+1}/{max_retries}: {e}")
                time.sleep(delay * (i + 1))
    return wrapper
