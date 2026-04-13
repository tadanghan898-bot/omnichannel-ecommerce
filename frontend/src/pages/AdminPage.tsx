import { useEffect, useState } from 'react'
import api from '../api/client'

export default function AdminPage() {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/api/admin/dashboard').then(r => { setData(r.data); setLoading(false) }).catch(() => setLoading(false))
  }, [])

  if (loading) return <div className="text-center py-20">Đang tải...</div>

  const s = data?.stats || {}

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Admin Dashboard</h1>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {[
          { label: 'Người dùng', value: s.total_users, color: 'blue' },
          { label: 'Sản phẩm', value: s.total_products, color: 'green' },
          { label: 'Đơn hàng', value: s.total_orders, color: 'purple' },
          { label: 'Doanh thu', value: (s.total_revenue || 0).toLocaleString('vi-VN') + 'đ', color: 'orange' },
        ].map(stat => (
          <div key={stat.label} className="bg-white rounded-xl p-6 shadow-sm">
            <div className="text-sm text-gray-500">{stat.label}</div>
            <div className={`text-2xl font-bold text-${stat.color}-600`}>{stat.value}</div>
          </div>
        ))}
      </div>

      {/* Orders by status */}
      <div className="bg-white rounded-xl p-6 mb-8">
        <h2 className="font-bold mb-4">Đơn hàng theo trạng thái</h2>
        <div className="grid grid-cols-3 md:grid-cols-6 gap-3">
          {Object.entries(s.orders_by_status || {}).map(([status, count]) => (
            <div key={status} className="text-center p-3 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold">{count}</div>
              <div className="text-xs text-gray-500 capitalize">{status}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Recent orders */}
      {data?.recent_orders?.length > 0 && (
        <div className="bg-white rounded-xl p-6">
          <h2 className="font-bold mb-4">Đơn hàng gần đây</h2>
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 border-b">
                <th className="pb-2">Mã</th><th className="pb-2">Tổng</th><th className="pb-2">Trạng thái</th><th className="pb-2">Ngày</th>
              </tr>
            </thead>
            <tbody>
              {data.recent_orders.map((o: any) => (
                <tr key={o.id} className="border-b">
                  <td className="py-2 font-medium">{o.order_number}</td>
                  <td className="py-2">{o.total.toLocaleString('vi-VN')}đ</td>
                  <td className="py-2 capitalize">{o.status}</td>
                  <td className="py-2 text-gray-500">{new Date(o.created_at).toLocaleDateString('vi-VN')}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
