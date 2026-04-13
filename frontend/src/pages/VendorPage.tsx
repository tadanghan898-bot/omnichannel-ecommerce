import { useEffect, useState } from 'react'
import api from '../api/client'

export default function VendorPage() {
  const [vendor, setVendor] = useState<any>(null)
  const [products, setProducts] = useState<any[]>([])
  const [analytics, setAnalytics] = useState<any>(null)
  const [tab, setTab] = useState('dashboard')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/api/vendors/me').then(r => { setVendor(r.data); setLoading(false) }).catch(() => setLoading(false))
    api.get('/api/vendors/me/analytics').then(r => setAnalytics(r.data)).catch(() => {})
    api.get('/api/vendors/me/products').then(r => setProducts(r.data.items || [])).catch(() => {})
  }, [])

  if (loading) return <div className="text-center py-20">Đang tải...</div>

  if (!vendor) return (
    <div className="max-w-2xl mx-auto px-4 py-16 text-center">
      <h2 className="text-xl font-bold mb-4">Bạn chưa đăng ký vendor</h2>
      <button className="btn-primary">Đăng ký Vendor</button>
    </div>
  )

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Vendor Dashboard: {vendor.store_name}</h1>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-white rounded-xl p-6 shadow-sm">
          <div className="text-sm text-gray-500">Tổng sản phẩm</div>
          <div className="text-2xl font-bold">{products.length}</div>
        </div>
        <div className="bg-white rounded-xl p-6 shadow-sm">
          <div className="text-sm text-gray-500">Doanh thu</div>
          <div className="text-2xl font-bold text-green-600">{((analytics?.total_revenue) || 0).toLocaleString('vi-VN')}đ</div>
        </div>
        <div className="bg-white rounded-xl p-6 shadow-sm">
          <div className="text-sm text-gray-500">Chờ thanh toán</div>
          <div className="text-2xl font-bold text-orange-600">{((analytics?.pending_payout) || 0).toLocaleString('vi-VN')}đ</div>
        </div>
        <div className="bg-white rounded-xl p-6 shadow-sm">
          <div className="text-sm text-gray-500">Đánh giá</div>
          <div className="text-2xl font-bold">{analytics?.rating?.toFixed(1) || '0.0'} ⭐</div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-4 mb-6 border-b">
        {['dashboard', 'products', 'orders'].map(t => (
          <button key={t} onClick={() => setTab(t)} className={`px-4 py-2 font-medium capitalize ${tab === t ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-500'}`}>{t}</button>
        ))}
      </div>

      {tab === 'products' && (
        <div className="bg-white rounded-xl">
          <div className="p-4 border-b flex justify-between items-center">
            <span className="font-bold">Quản lý sản phẩm ({products.length})</span>
            <button className="btn-primary text-sm">+ Thêm sản phẩm</button>
          </div>
          {products.length === 0 ? (
            <div className="p-8 text-center text-gray-500">Chưa có sản phẩm nào</div>
          ) : (
            <table className="w-full text-sm">
              <thead><tr className="text-left text-gray-500 bg-gray-50"><th className="p-3">Sản phẩm</th><th className="p-3">Giá</th><th className="p-3">Tồn kho</th><th className="p-3">Trạng thái</th></tr></thead>
              <tbody>
                {products.map(p => (
                  <tr key={p.id} className="border-t">
                    <td className="p-3">{p.name}</td>
                    <td className="p-3">{p.price.toLocaleString('vi-VN')}đ</td>
                    <td className="p-3">{p.stock}</td>
                    <td className="p-3"><span className={`px-2 py-0.5 rounded text-xs ${p.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'}`}>{p.status}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {tab === 'dashboard' && (
        <div className="bg-white rounded-xl p-6">
          <h3 className="font-bold mb-4">Thông tin cửa hàng</h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div><span className="text-gray-500">Tên cửa hàng:</span> {vendor.store_name}</div>
            <div><span className="text-gray-500">Trạng thái:</span> <span className="capitalize">{vendor.status}</span></div>
          </div>
        </div>
      )}
    </div>
  )
}
