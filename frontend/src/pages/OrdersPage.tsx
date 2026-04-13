import { useEffect, useState } from 'react'
import api from '../api/client'

interface Order {
  id: number; order_number: string; status: string; payment_status: string; total: number; created_at: string; items?: any[]
}

const statusLabels: Record<string, string> = {
  pending: 'Chờ xác nhận', confirmed: 'Đã xác nhận', processing: 'Đang xử lý',
  shipped: 'Đã gửi', delivered: 'Đã giao', cancelled: 'Đã hủy', refunded: 'Đã hoàn tiền'
}
const statusColors: Record<string, string> = {
  pending: 'bg-yellow-100 text-yellow-700', confirmed: 'bg-blue-100 text-blue-700',
  processing: 'bg-purple-100 text-purple-700', shipped: 'bg-indigo-100 text-indigo-700',
  delivered: 'bg-green-100 text-green-700', cancelled: 'bg-red-100 text-red-700', refunded: 'bg-gray-100 text-gray-700'
}

export default function OrdersPage() {
  const [orders, setOrders] = useState<Order[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedOrder, setSelectedOrder] = useState<number | null>(null)

  useEffect(() => {
    api.get('/api/auth/orders').then(r => { setOrders(r.data); setLoading(false) }).catch(() => setLoading(false))
  }, [])

  if (loading) return <div className="text-center py-20">Đang tải...</div>

  if (orders.length === 0) return (
    <div className="max-w-4xl mx-auto px-4 py-16 text-center">
      <h2 className="text-xl font-bold mb-2">Chưa có đơn hàng nào</h2>
      <p className="text-gray-500">Hãy bắt đầu mua sắm ngay!</p>
    </div>
  )

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Đơn hàng của tôi</h1>
      <div className="space-y-4">
        {orders.map(o => (
          <div key={o.id} className="bg-white rounded-xl p-4">
            <div className="flex justify-between items-center cursor-pointer" onClick={() => setSelectedOrder(selectedOrder === o.id ? null : o.id)}>
              <div>
                <div className="font-bold">{o.order_number}</div>
                <div className="text-sm text-gray-500">{new Date(o.created_at).toLocaleDateString('vi-VN')} | <span className={`px-2 py-0.5 rounded text-xs ${statusColors[o.status]}`}>{statusLabels[o.status]}</span></div>
              </div>
              <div className="text-right">
                <div className="font-bold">{o.total.toLocaleString('vi-VN')}đ</div>
                <div className="text-xs text-gray-500">{o.payment_status === 'paid' ? 'Đã thanh toán' : 'Chưa thanh toán'}</div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
