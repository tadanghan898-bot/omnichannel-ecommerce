import { useState, useEffect } from "react";
import { api } from "../api/client";

interface UnifiedOrder {
  platform: string;
  platform_order_id: string;
  customer_name: string;
  customer_phone: string;
  shipping_address: string;
  items: any[];
  total_amount: number;
  status: string;
  created_at: string;
  tracking_number: string;
  payment_method: string;
}

interface PlatformSummary {
  connected: boolean;
  status: string;
  error?: string;
}

const PLATFORM_COLORS: Record<string, string> = {
  shopee: "bg-orange-500",
  lazada: "bg-red-500",
  tiktok: "bg-pink-600",
  facebook: "bg-blue-600",
  sendo: "bg-violet-600",
};

const STATUS_COLORS: Record<string, string> = {
  pending: "bg-yellow-100 text-yellow-800",
  unpaid: "bg-yellow-100 text-yellow-800",
  waiting_payment: "bg-yellow-100 text-yellow-800",
  confirmed: "bg-blue-100 text-blue-800",
  ready_to_ship: "bg-blue-100 text-blue-800",
  shipped: "bg-indigo-100 text-indigo-800",
  in_transit: "bg-indigo-100 text-indigo-800",
  delivered: "bg-green-100 text-green-800",
  completed: "bg-green-100 text-green-800",
  cancelled: "bg-red-100 text-red-800",
};

export default function OrderHubPage() {
  const [orders, setOrders] = useState<UnifiedOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterPlatform, setFilterPlatform] = useState<string>("all");
  const [filterStatus, setFilterStatus] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [platforms, setPlatforms] = useState<Record<string, PlatformSummary>>({});
  const [activeTab, setActiveTab] = useState<"orders" | "platforms">("orders");

  useEffect(() => {
    fetchOrders();
    fetchPlatformStatus();
  }, []);

  const fetchOrders = async () => {
    setLoading(true);
    try {
      const resp = await api.get("/api/integrations/unified/orders");
      if (resp.data?.orders) {
        setOrders(resp.data.orders);
      }
    } catch {
      // demo data fallback
      setOrders(DEMO_ORDERS);
    }
    setLoading(false);
  };

  const fetchPlatformStatus = async () => {
    try {
      const resp = await api.get("/api/integrations/platforms/status");
      if (resp.data) {
        setPlatforms(resp.data);
      }
    } catch {
      setPlatforms(DEMO_PLATFORMS);
    }
  };

  const syncOrders = async (platform?: string) => {
    const endpoint = platform
      ? `/api/integrations/${platform}/sync/orders`
      : "/api/integrations/unified/sync";
    await api.post(endpoint);
    await fetchOrders();
  };

  const filteredOrders = orders.filter((order) => {
    if (filterPlatform !== "all" && order.platform !== filterPlatform) return false;
    if (filterStatus !== "all" && order.status !== filterStatus) return false;
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      return (
        order.platform_order_id.toLowerCase().includes(q) ||
        order.customer_name.toLowerCase().includes(q) ||
        order.customer_phone.includes(q)
      );
    }
    return true;
  });

  const totalRevenue = filteredOrders.reduce((sum, o) => sum + (o.total_amount || 0), 0);
  const platformCounts = orders.reduce((acc, o) => {
    acc[o.platform] = (acc[o.platform] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Order Hub</h1>
          <p className="text-gray-500 mt-1">Unified orders from all marketplace platforms</p>
        </div>
        <button
          onClick={() => syncOrders()}
          className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 flex items-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Sync All
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
        <div className="bg-white rounded-xl shadow-sm p-4 border">
          <p className="text-sm text-gray-500">Total Orders</p>
          <p className="text-2xl font-bold">{orders.length}</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm p-4 border">
          <p className="text-sm text-gray-500">Total Revenue</p>
          <p className="text-2xl font-bold">{totalRevenue.toLocaleString()}₫</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm p-4 border">
          <p className="text-sm text-gray-500">Shopee</p>
          <p className="text-2xl font-bold text-orange-500">{platformCounts.shopee || 0}</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm p-4 border">
          <p className="text-sm text-gray-500">Lazada</p>
          <p className="text-2xl font-bold text-red-500">{platformCounts.lazada || 0}</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm p-4 border">
          <p className="text-sm text-gray-500">TikTok</p>
          <p className="text-2xl font-bold text-pink-600">{platformCounts.tiktok || 0}</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-4 border-b mb-6">
        <button
          onClick={() => setActiveTab("orders")}
          className={`pb-3 px-1 font-medium ${activeTab === "orders" ? "border-b-2 border-indigo-600 text-indigo-600" : "text-gray-500"}`}
        >
          Orders ({filteredOrders.length})
        </button>
        <button
          onClick={() => setActiveTab("platforms")}
          className={`pb-3 px-1 font-medium ${activeTab === "platforms" ? "border-b-2 border-indigo-600 text-indigo-600" : "text-gray-500"}`}
        >
          Platforms
        </button>
      </div>

      {activeTab === "orders" && (
        <>
          {/* Filters */}
          <div className="flex flex-wrap gap-4 mb-6">
            <input
              type="text"
              placeholder="Search orders..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="border rounded-lg px-3 py-2 flex-1 min-w-64"
            />
            <select
              value={filterPlatform}
              onChange={(e) => setFilterPlatform(e.target.value)}
              className="border rounded-lg px-3 py-2"
            >
              <option value="all">All Platforms</option>
              <option value="shopee">Shopee</option>
              <option value="lazada">Lazada</option>
              <option value="tiktok">TikTok Shop</option>
              <option value="facebook">Facebook Shops</option>
              <option value="sendo">Sendo</option>
            </select>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="border rounded-lg px-3 py-2"
            >
              <option value="all">All Status</option>
              <option value="pending">Pending</option>
              <option value="confirmed">Confirmed</option>
              <option value="shipped">Shipped</option>
              <option value="delivered">Delivered</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>

          {/* Orders Table */}
          {loading ? (
            <div className="text-center py-12 text-gray-500">Loading orders...</div>
          ) : filteredOrders.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              No orders found. Connect your marketplace accounts to start syncing.
            </div>
          ) : (
            <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Order ID</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Platform</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Customer</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Amount</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Status</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Date</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {filteredOrders.map((order, i) => (
                    <tr key={i} className="hover:bg-gray-50">
                      <td className="px-4 py-3 text-sm font-mono">
                        {order.platform_order_id || "—"}
                      </td>
                      <td className="px-4 py-3">
                        <span className={`${PLATFORM_COLORS[order.platform] || "bg-gray-500"} text-white text-xs px-2 py-1 rounded`}>
                          {order.platform}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm">
                        <div className="font-medium">{order.customer_name || "—"}</div>
                        <div className="text-gray-500 text-xs">{order.customer_phone}</div>
                      </td>
                      <td className="px-4 py-3 text-sm font-medium">
                        {order.total_amount?.toLocaleString()}₫
                      </td>
                      <td className="px-4 py-3">
                        <span className={`text-xs px-2 py-1 rounded-full ${STATUS_COLORS[order.status?.toLowerCase()] || "bg-gray-100 text-gray-800"}`}>
                          {order.status || "—"}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-500">
                        {order.created_at ? new Date(order.created_at).toLocaleDateString("vi-VN") : "—"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}

      {activeTab === "platforms" && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {Object.entries({
            shopee: { name: "Shopee", color: "bg-orange-500", icon: "🛒" },
            lazada: { name: "Lazada", color: "bg-red-500", icon: "🏪" },
            tiktok: { name: "TikTok Shop", color: "bg-pink-600", icon: "🎵" },
            facebook: { name: "Facebook Shops", color: "bg-blue-600", icon: "📘" },
            sendo: { name: "Sendo", color: "bg-violet-600", icon: "🛍️" },
          }).map(([key, platform]) => {
            const status = platforms[key];
            return (
              <div key={key} className="bg-white rounded-xl shadow-sm border p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className={`${platform.color} text-white w-12 h-12 rounded-xl flex items-center justify-center text-xl`}>
                    {platform.icon}
                  </div>
                  <div>
                    <h3 className="font-semibold text-lg">{platform.name}</h3>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${status?.connected ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"}`}>
                      {status?.connected ? "Connected" : "Not connected"}
                    </span>
                  </div>
                </div>
                <div className="space-y-2 text-sm text-gray-600">
                  <div className="flex justify-between">
                    <span>Orders synced:</span>
                    <span className="font-medium">{platformCounts[key] || 0}</span>
                  </div>
                </div>
                <button
                  onClick={() => syncOrders(key)}
                  className="mt-4 w-full bg-gray-100 hover:bg-gray-200 text-gray-700 py-2 rounded-lg text-sm font-medium"
                >
                  Sync Orders
                </button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

const DEMO_ORDERS: UnifiedOrder[] = [
  {
    platform: "shopee",
    platform_order_id: "SP2610080001",
    customer_name: "Nguyen Van A",
    customer_phone: "0901234567",
    shipping_address: "123 Nguyen Trai, Q1, TP.HCM",
    items: [{ name: "Wireless Earbuds", quantity: 1, price: 299000 }],
    total_amount: 299000,
    status: "ready_to_ship",
    created_at: new Date(Date.now() - 86400000).toISOString(),
    tracking_number: "",
    payment_method: "COD",
  },
  {
    platform: "lazada",
    platform_order_id: "LZ2610080002",
    customer_name: "Tran Thi B",
    customer_phone: "0912345678",
    shipping_address: "45 Le Duan, Q.3, TP.HCM",
    items: [{ name: "Smart Watch Pro", quantity: 1, price: 899000 }],
    total_amount: 899000,
    status: "shipped",
    created_at: new Date(Date.now() - 172800000).toISOString(),
    tracking_number: "LAZ123456789",
    payment_method: "Wallet",
  },
  {
    platform: "tiktok",
    platform_order_id: "TT2610080003",
    customer_name: "Le Van C",
    customer_phone: "0923456789",
    shipping_address: "78 Dien Bien Phu, Q.Binh Thanh, TP.HCM",
    items: [{ name: "Portable Charger 20000mAh", quantity: 2, price: 450000 }],
    total_amount: 900000,
    status: "waiting_payment",
    created_at: new Date(Date.now() - 3600000).toISOString(),
    tracking_number: "",
    payment_method: "TikPay",
  },
  {
    platform: "shopee",
    platform_order_id: "SP2610080004",
    customer_name: "Pham Thi D",
    customer_phone: "0934567890",
    shipping_address: "12 Thai Binh, Q.5, TP.HCM",
    items: [{ name: "Bluetooth Speaker", quantity: 1, price: 550000 }],
    total_amount: 550000,
    status: "completed",
    created_at: new Date(Date.now() - 604800000).toISOString(),
    tracking_number: "SP789012345",
    payment_method: "COD",
  },
  {
    platform: "facebook",
    platform_order_id: "FB2610080005",
    customer_name: "Hoang Van E",
    customer_phone: "0945678901",
    shipping_address: "56 Truong Chinh, Q.Tan Binh, TP.HCM",
    items: [{ name: "USB-C Hub 7-in-1", quantity: 1, price: 699000 }],
    total_amount: 699000,
    status: "confirmed",
    created_at: new Date(Date.now() - 43200000).toISOString(),
    tracking_number: "",
    payment_method: "Direct",
  },
];

const DEMO_PLATFORMS: Record<string, PlatformSummary> = {
  shopee: { connected: true, status: "active" },
  lazada: { connected: true, status: "active" },
  tiktok: { connected: false, status: "disconnected" },
  facebook: { connected: false, status: "disconnected" },
  sendo: { connected: false, status: "disconnected" },
};
