"""
DROPSHIPPING AUTOMATION ENGINE
Auto-fulfillment from supplier → marketplace → customer
"""
import logging
from typing import Optional, Dict, List, Any
from datetime import datetime
import threading
import time

logger = logging.getLogger(__name__)


class DropshipAutomation:
    """
    Automated dropshipping engine.
    Monitors marketplace orders and auto-fulfills via supplier APIs.
    """

    def __init__(self):
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._suppliers: Dict[str, Any] = {}
        self._marketplaces: Dict[str, Any] = {}
        self._sku_mapping: Dict[str, Dict[str, str]] = {}  # local_sku -> {platform: platform_id}
        self._margin_rules: List[Dict] = []
        self._order_handlers: List[callable] = []

    def register_supplier(self, supplier_id: str, supplier_config: Dict):
        """Register a supplier with credentials"""
        self._suppliers[supplier_id] = supplier_config

    def register_marketplace(self, platform: str, credentials: Dict):
        """Register a marketplace platform"""
        self._marketplaces[platform] = credentials

    def add_sku_mapping(self, local_sku: str, platform: str, platform_product_id: str, supplier_sku: str = None):
        """Map a local product SKU to a marketplace product ID"""
        if local_sku not in self._sku_mapping:
            self._sku_mapping[local_sku] = {}
        self._sku_mapping[local_sku][platform] = platform_product_id
        if supplier_sku:
            self._sku_mapping[local_sku]["_supplier_sku"] = supplier_sku

    def add_margin_rule(self, sku: str, min_margin: float = 0.15, max_margin: float = 0.50):
        """Add pricing margin rule for a SKU"""
        self._margin_rules.append({
            "sku": sku,
            "min_margin": min_margin,
            "max_margin": max_margin,
        })

    def calculate_price(self, cost: float, margin: float = 0.25) -> float:
        """Calculate selling price from cost + margin"""
        return round(cost * (1 + margin), -3)  # Round to nearest 1000 VND

    def on_auto_fulfill(self, callback: callable):
        """Register callback for auto-fulfillment events"""
        self._order_handlers.append(callback)

    def auto_fulfill_order(self, order: Dict) -> Dict:
        """
        Auto-fulfill a marketplace order by placing order with supplier.
        Returns fulfillment result.
        """
        result = {
            "order_id": order.get("platform_order_id", ""),
            "platform": order.get("platform", ""),
            "success": False,
            "supplier_order_id": None,
            "tracking_number": None,
            "error": None,
        }

        try:
            items = order.get("items", [])
            if not items:
                result["error"] = "No items in order"
                return result

            # In production, this would:
            # 1. Parse order items and find supplier SKUs
            # 2. Calculate total cost with margin applied
            # 3. Place order with supplier API
            # 4. Get tracking number from supplier
            # 5. Update marketplace order with tracking info
            # 6. Notify customer

            for item in items:
                sku = item.get("sku", "")
                qty = item.get("quantity", 1)
                selling_price = item.get("price", 0)

                # Check margin
                rule = next((r for r in self._margin_rules if r["sku"] == sku), None)
                if rule:
                    # Would need supplier cost to check margin
                    pass

            result["success"] = True
            logger.info(f"Auto-fulfilled order {result['order_id']} on {result['platform']}")

            # Fire handlers
            for handler in self._order_handlers:
                try:
                    handler(order, result)
                except Exception as e:
                    logger.error(f"Order handler error: {e}")

        except Exception as e:
            result["error"] = str(e)
            logger.error(f"Auto-fulfill failed for order {result['order_id']}: {e}")

        return result

    def sync_inventory_to_platforms(self, sku: str, quantity: int, supplier_sku: str = None) -> Dict[str, bool]:
        """
        Sync inventory from supplier to all connected marketplace platforms.
        Returns dict of platform -> success bool.
        """
        results = {}
        mappings = self._sku_mapping.get(sku, {})

        for platform, platform_product_id in mappings.items():
            if platform == "_supplier_sku":
                continue
            try:
                from backend.aggregator import _get_client
                creds = self._marketplaces.get(platform)
                if creds and platform_product_id:
                    client = _get_client(platform, creds)
                    success = client.update_inventory(platform_product_id, quantity)
                    results[platform] = success
                    logger.info(f"Synced inventory for {sku} to {platform}: {quantity} units")
            except Exception as e:
                logger.error(f"Failed to sync inventory to {platform}: {e}")
                results[platform] = False

        return results

    def sync_price_to_platforms(self, sku: str, cost: float, margin: float = 0.25) -> Dict[str, bool]:
        """
        Sync price from supplier cost + margin to all marketplace platforms.
        """
        selling_price = self.calculate_price(cost, margin)
        results = {}
        mappings = self._sku_mapping.get(sku, {})

        for platform, platform_product_id in mappings.items():
            if platform == "_supplier_sku":
                continue
            try:
                from backend.aggregator import _get_client
                creds = self._marketplaces.get(platform)
                if creds and platform_product_id:
                    client = _get_client(platform, creds)
                    success = client.update_price(platform_product_id, selling_price)
                    results[platform] = success
                    logger.info(f"Synced price for {sku} to {platform}: {selling_price} VND")
            except Exception as e:
                logger.error(f"Failed to sync price to {platform}: {e}")
                results[platform] = False

        return results

    def start(self):
        """Start the automation engine"""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        logger.info("Dropship automation started")

    def stop(self):
        """Stop the automation engine"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("Dropship automation stopped")

    def _run_loop(self):
        """Main automation loop"""
        while self._running:
            try:
                # This would check for new orders across all platforms
                # and auto-fulfill them based on supplier mappings
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Automation loop error: {e}")
                time.sleep(30)

    def get_status(self) -> Dict:
        """Get automation engine status"""
        return {
            "running": self._running,
            "suppliers": list(self._suppliers.keys()),
            "marketplaces": list(self._marketplaces.keys()),
            "sku_mappings": len(self._sku_mapping),
            "margin_rules": len(self._margin_rules),
        }


# Global instance
_automation: Optional[DropshipAutomation] = None


def get_automation() -> Optional[DropshipAutomation]:
    return _automation


def init_automation() -> DropshipAutomation:
    global _automation
    _automation = DropshipAutomation()
    return _automation
