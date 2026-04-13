"""
OMNICHANNEL SYNC SCHEDULER
Background polling + webhook handlers for order/inventory sync across platforms
"""
import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Callable
from threading import Thread, Event

logger = logging.getLogger(__name__)


class SyncScheduler:
    """Background scheduler for syncing orders and inventory across marketplace platforms"""

    def __init__(
        self,
        order_poll_interval: int = 120,  # seconds between order polls
        inventory_poll_interval: int = 300,  # seconds between inventory checks
        auto_fulfill: bool = False,
    ):
        self.order_poll_interval = order_poll_interval
        self.inventory_poll_interval = inventory_poll_interval
        self.auto_fulfill = auto_fulfill
        self._stop_event = Event()
        self._thread: Optional[Thread] = None
        self._order_callbacks: List[Callable] = []
        self._inventory_callbacks: List[Callable] = []
        self._last_order_sync: Dict[str, float] = {}
        self._last_inventory_sync: Dict[str, float] = {}
        self._platform_credentials: Dict[str, Dict] = {}

    def register_platform(self, platform: str, credentials: Dict):
        """Register a marketplace platform with credentials"""
        self._platform_credentials[platform] = credentials
        self._last_order_sync[platform] = 0
        self._last_inventory_sync[platform] = 0

    def on_new_orders(self, callback: Callable):
        """Register callback for new orders detected during sync"""
        self._order_callbacks.append(callback)

    def on_inventory_change(self, callback: Callable):
        """Register callback for inventory changes detected"""
        self._inventory_callbacks.append(callback)

    def _sync_orders(self, platform: str, credentials: Dict):
        """Sync orders for a single platform"""
        try:
            from backend.aggregator import _get_client
            client = _get_client(platform, credentials)
            orders = client.get_orders(page_size=50)

            last_sync = self._last_order_sync.get(platform, 0)
            new_orders = []

            for order in orders:
                created = order.get("created_at", "")
                if isinstance(created, str):
                    try:
                        ts = datetime.fromisoformat(created.replace("Z", "+00:00")).timestamp()
                    except (ValueError, TypeError):
                        ts = time.time()
                else:
                    ts = created or time.time()

                if ts > last_sync:
                    new_orders.append(order)

            if new_orders:
                logger.info(f"[{platform}] Found {len(new_orders)} new orders")
                for cb in self._order_callbacks:
                    try:
                        cb(platform, new_orders)
                    except Exception as e:
                        logger.error(f"Order sync callback error: {e}")

            self._last_order_sync[platform] = time.time()
        except Exception as e:
            logger.error(f"[{platform}] Order sync failed: {e}")

    def _sync_inventory(self, platform: str, credentials: Dict):
        """Sync inventory for a single platform"""
        try:
            from backend.aggregator import _get_client
            client = _get_client(platform, credentials)
            products = client.get_products(page_size=50)

            inventory_map = {}
            for p in products:
                sku = p.get("sku", "")
                stock = p.get("stock", 0)
                if sku:
                    inventory_map[sku] = stock

            if inventory_map:
                for cb in self._inventory_callbacks:
                    try:
                        cb(platform, inventory_map)
                    except Exception as e:
                        logger.error(f"Inventory sync callback error: {e}")

            self._last_inventory_sync[platform] = time.time()
        except Exception as e:
            logger.error(f"[{platform}] Inventory sync failed: {e}")

    def _run_loop(self):
        """Main sync loop running in background thread"""
        logger.info("Sync scheduler started")
        while not self._stop_event.is_set():
            now = time.time()

            # Order sync
            for platform, credentials in self._platform_credentials.items():
                last_order = self._last_order_sync.get(platform, 0)
                if now - last_order >= self.order_poll_interval:
                    self._sync_orders(platform, credentials)

            # Inventory sync
            for platform, credentials in self._platform_credentials.items():
                last_inv = self._last_inventory_sync.get(platform, 0)
                if now - last_inv >= self.inventory_poll_interval:
                    self._sync_inventory(platform, credentials)

            # Sleep in small increments to allow quick shutdown
            self._stop_event.wait(timeout=10)

        logger.info("Sync scheduler stopped")

    def start(self):
        """Start the background sync scheduler"""
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = Thread(target=self._run_loop, daemon=True, name="SyncScheduler")
        self._thread.start()
        logger.info("Sync scheduler thread started")

    def stop(self):
        """Stop the background sync scheduler"""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("Sync scheduler thread stopped")

    def sync_now(self, platform: Optional[str] = None):
        """Trigger immediate sync for one or all platforms"""
        if platform:
            creds = self._platform_credentials.get(platform)
            if creds:
                self._sync_orders(platform, creds)
                self._sync_inventory(platform, creds)
        else:
            for p, creds in self._platform_credentials.items():
                self._sync_orders(p, creds)
                self._sync_inventory(p, creds)

    def get_status(self) -> Dict:
        """Get sync status for all platforms"""
        now = time.time()
        return {
            "running": self._thread is not None and self._thread.is_alive(),
            "platforms": list(self._platform_credentials.keys()),
            "order_sync_intervals": {
                p: now - self._last_order_sync.get(p, 0) for p in self._platform_credentials
            },
            "inventory_sync_intervals": {
                p: now - self._last_inventory_sync.get(p, 0) for p in self._platform_credentials
            },
        }


# Global scheduler instance
_scheduler: Optional[SyncScheduler] = None


def get_scheduler() -> Optional[SyncScheduler]:
    return _scheduler


def init_scheduler(
    platform_credentials: Dict[str, Dict],
    order_poll_interval: int = 120,
    inventory_poll_interval: int = 300,
    auto_fulfill: bool = False,
) -> SyncScheduler:
    global _scheduler
    _scheduler = SyncScheduler(
        order_poll_interval=order_poll_interval,
        inventory_poll_interval=inventory_poll_interval,
        auto_fulfill=auto_fulfill,
    )
    for platform, creds in platform_credentials.items():
        _scheduler.register_platform(platform, creds)
    return _scheduler


# === WEBHOOK HANDLERS ===
# These handle incoming webhooks from marketplace platforms


def handle_shopee_webhook(payload: Dict) -> Dict:
    """Handle Shopee webhook notification"""
    code = payload.get("code", 0)
    if code == 1:  # New order
        return {"action": "process_order", "order_id": payload.get("order_sn")}
    elif code == 3:  # Order shipped
        return {"action": "update_tracking", "order_id": payload.get("order_sn")}
    return {"action": "unknown"}


def handle_lazada_webhook(payload: Dict) -> Dict:
    """Handle Lazada webhook notification"""
    notification_type = payload.get("notification_type", "")
    if notification_type == "order_created":
        return {"action": "process_order", "order_id": payload.get("order_id")}
    elif notification_type == "order_shipped":
        return {"action": "update_tracking", "order_id": payload.get("order_id")}
    return {"action": "unknown"}


def handle_tiktok_webhook(payload: Dict) -> Dict:
    """Handle TikTok Shop webhook notification"""
    event_type = payload.get("event_type", "")
    if "order" in event_type.lower():
        return {"action": "process_order", "order_id": payload.get("order_id")}
    return {"action": "unknown"}


def handle_facebook_webhook(payload: Dict) -> Dict:
    """Handle Facebook webhook notification"""
    entry = payload.get("entry", [{}])[0]
    changes = entry.get("changes", [])
    if changes:
        change = changes[0]
        if change.get("field") == "commerce_orders":
            return {"action": "process_order", "order_id": change.get("value", {}).get("id")}
    return {"action": "unknown"}
