import { useState } from "react";
import api from "../../api/client";

const PLATFORMS = [
  {
    id: "shopee",
    name: "Shopee",
    icon: "🛒",
    color: "bg-orange-500",
    description: "Connect your Shopee Seller account to sync orders and products",
    fields: [
      { name: "partner_id", label: "Partner ID", placeholder: "Your Shopee Partner ID" },
      { name: "partner_key", label: "Partner Key", placeholder: "Your Shopee Partner Key", type: "password" },
      { name: "shop_id", label: "Shop ID", placeholder: "Your Shopee Shop ID" },
      { name: "access_token", label: "Access Token", placeholder: "OAuth Access Token", type: "password" },
    ],
  },
  {
    id: "lazada",
    name: "Lazada",
    icon: "🏪",
    color: "bg-red-500",
    description: "Connect your Lazada Seller account to sync orders and products",
    fields: [
      { name: "app_key", label: "App Key", placeholder: "Your Lazada App Key" },
      { name: "app_secret", label: "App Secret", placeholder: "Your Lazada App Secret", type: "password" },
      { name: "access_token", label: "Access Token", placeholder: "OAuth Access Token", type: "password" },
      { name: "country", label: "Country", placeholder: "vn (default)", default: "vn" },
    ],
  },
  {
    id: "tiktok",
    name: "TikTok Shop",
    icon: "🎵",
    color: "bg-pink-600",
    description: "Connect your TikTok Shop Seller account to sync orders and products",
    fields: [
      { name: "app_key", label: "App Key", placeholder: "Your TikTok App Key" },
      { name: "app_secret", label: "App Secret", placeholder: "Your TikTok App Secret", type: "password" },
      { name: "access_token", label: "Access Token", placeholder: "OAuth Access Token", type: "password" },
      { name: "shop_id", label: "Shop ID", placeholder: "Your TikTok Shop ID" },
      { name: "region", label: "Region", placeholder: "VN (default)", default: "VN" },
    ],
  },
  {
    id: "facebook",
    name: "Facebook Shops",
    icon: "📘",
    color: "bg-blue-600",
    description: "Connect your Facebook/Meta Commerce account to sync products",
    fields: [
      { name: "app_id", label: "App ID", placeholder: "Facebook App ID" },
      { name: "app_secret", label: "App Secret", placeholder: "Facebook App Secret", type: "password" },
      { name: "access_token", label: "Access Token", placeholder: "Page Access Token", type: "password" },
      { name: "page_id", label: "Page ID", placeholder: "Facebook Page ID" },
      { name: "catalog_id", label: "Catalog ID", placeholder: "Commerce Catalog ID (optional)" },
    ],
  },
  {
    id: "sendo",
    name: "Sendo",
    icon: "🛍️",
    color: "bg-violet-600",
    description: "Connect your Sendo.vn Seller account to sync orders and products",
    fields: [
      { name: "partner_id", label: "Partner ID", placeholder: "Your Sendo Partner ID" },
      { name: "partner_key", label: "Partner Key", placeholder: "Your Sendo Partner Key", type: "password" },
      { name: "shop_id", label: "Shop ID", placeholder: "Your Sendo Shop ID" },
    ],
  },
];

export default function MarketplacePage() {
  const [activeConnect, setActiveConnect] = useState<string | null>(null);
  const [formData, setFormData] = useState<Record<string, string>>({});
  const [connecting, setConnecting] = useState(false);
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);
  const [connectedPlatforms, setConnectedPlatforms] = useState<Record<string, boolean>>({
    shopee: false,
    lazada: false,
    tiktok: false,
    facebook: false,
    sendo: false,
  });

  const handleConnect = async (platformId: string) => {
    setConnecting(true);
    setMessage(null);
    try {
      const endpoint = `/api/integrations/${platformId}/connect`;
      const resp = await api.post(endpoint, formData);
      if (resp.data?.status === "connected") {
        setMessage({ type: "success", text: `${PLATFORMS.find(p => p.id === platformId)?.name} connected successfully!` });
        setConnectedPlatforms(prev => ({ ...prev, [platformId]: true }));
        setActiveConnect(null);
        setFormData({});
      } else {
        setMessage({ type: "error", text: resp.data?.message || "Connection failed" });
      }
    } catch (err: any) {
      setMessage({ type: "error", text: err?.response?.data?.detail || "Connection failed. Check your credentials." });
    }
    setConnecting(false);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Marketplace Hub</h1>
        <p className="text-gray-500 mt-1">Connect and manage all your marketplace seller accounts in one place</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
        <div className="bg-white rounded-xl shadow-sm p-4 border">
          <p className="text-sm text-gray-500">Connected</p>
          <p className="text-2xl font-bold text-green-600">{Object.values(connectedPlatforms).filter(Boolean).length}</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm p-4 border">
          <p className="text-sm text-gray-500">Total Platforms</p>
          <p className="text-2xl font-bold">{PLATFORMS.length}</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm p-4 border">
          <p className="text-sm text-gray-500">Orders Today</p>
          <p className="text-2xl font-bold">—</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm p-4 border">
          <p className="text-sm text-gray-500">Products Synced</p>
          <p className="text-2xl font-bold">—</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm p-4 border">
          <p className="text-sm text-gray-500">Sync Status</p>
          <p className="text-2xl font-bold text-indigo-600">Ready</p>
        </div>
      </div>

      {/* Message */}
      {message && (
        <div className={`mb-6 p-4 rounded-lg ${message.type === "success" ? "bg-green-50 text-green-700" : "bg-red-50 text-red-700"}`}>
          {message.text}
        </div>
      )}

      {/* Platform Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {PLATFORMS.map((platform) => (
          <div key={platform.id} className="bg-white rounded-xl shadow-sm border overflow-hidden">
            <div className={`${platform.color} text-white p-6`}>
              <div className="flex items-center gap-3">
                <span className="text-3xl">{platform.icon}</span>
                <div>
                  <h3 className="text-xl font-bold">{platform.name}</h3>
                  <span className={`text-xs px-2 py-0.5 rounded-full ${connectedPlatforms[platform.id] ? "bg-white/20" : "bg-white/10"}`}>
                    {connectedPlatforms[platform.id] ? "✓ Connected" : "Not connected"}
                  </span>
                </div>
              </div>
            </div>
            <div className="p-6">
              <p className="text-sm text-gray-600 mb-4">{platform.description}</p>

              {activeConnect === platform.id ? (
                <div className="space-y-3">
                  {platform.fields.map((field) => (
                    <div key={field.name}>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        {field.label}
                      </label>
                      <input
                        type={field.type || "text"}
                        placeholder={field.placeholder}
                        defaultValue={field.default || ""}
                        onChange={(e) => setFormData(prev => ({ ...prev, [field.name]: e.target.value }))}
                        className="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                      />
                    </div>
                  ))}
                  <div className="flex gap-2 mt-4">
                    <button
                      onClick={() => handleConnect(platform.id)}
                      disabled={connecting}
                      className="flex-1 bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-700 disabled:opacity-50 font-medium"
                    >
                      {connecting ? "Connecting..." : "Connect"}
                    </button>
                    <button
                      onClick={() => { setActiveConnect(null); setFormData({}); }}
                      className="px-4 py-2 border rounded-lg hover:bg-gray-50 text-sm"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                <div className="space-y-2">
                  <button
                    onClick={() => setActiveConnect(platform.id)}
                    className={`w-full py-2 rounded-lg font-medium ${connectedPlatforms[platform.id] ? "bg-gray-100 text-gray-700 hover:bg-gray-200" : "bg-indigo-600 text-white hover:bg-indigo-700"}`}
                  >
                    {connectedPlatforms[platform.id] ? "Reconnect" : "Connect Account"}
                  </button>
                  {connectedPlatforms[platform.id] && (
                    <>
                      <button className="w-full py-2 border rounded-lg hover:bg-gray-50 text-sm">
                        Sync Orders
                      </button>
                      <button className="w-full py-2 border rounded-lg hover:bg-gray-50 text-sm">
                        Sync Products
                      </button>
                      <button className="w-full py-2 border rounded-lg hover:bg-gray-50 text-sm text-red-600">
                        Disconnect
                      </button>
                    </>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Docs */}
      <div className="mt-8 bg-blue-50 rounded-xl p-6 border border-blue-100">
        <h3 className="font-semibold text-blue-900 mb-2">How to get API credentials</h3>
        <div className="text-sm text-blue-700 space-y-1">
          <p><strong>Shopee:</strong> Register at <a href="https://partner.shopeemobile.com" className="underline" target="_blank" rel="noopener">partner.shopeemobile.com</a> → Create App → Get Partner ID, Key, Shop ID</p>
          <p><strong>Lazada:</strong> Apply at <a href="https://open.lazada.com" className="underline" target="_blank" rel="noopener">open.lazada.com</a> → Create App → Get App Key, Secret, Token</p>
          <p><strong>TikTok:</strong> Apply at <a href="https://partner.tiktokshop.com" className="underline" target="_blank" rel="noopener">partner.tiktokshop.com</a></p>
          <p><strong>Facebook:</strong> Create app at <a href="https://developers.facebook.com" className="underline" target="_blank" rel="noopener">developers.facebook.com</a> → Commerce API</p>
          <p><strong>Sendo:</strong> Contact <a href="https://open.sendo.vn" className="underline" target="_blank" rel="noopener">open.sendo.vn</a> for partner credentials</p>
        </div>
      </div>
    </div>
  );
}
