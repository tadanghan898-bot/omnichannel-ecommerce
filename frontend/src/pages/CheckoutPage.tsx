import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api/client'
import { useCartStore } from '../stores/cartStore'

export default function CheckoutPage() {
  const { subtotal } = useCartStore()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [form, setForm] = useState({
    shipping_name: '', shipping_phone: '', shipping_address: '', shipping_city: '',
    coupon_code: '', payment_method: 'cod', customer_note: ''
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      const res = await api.post('/api/orders', {
        items: [{ product_id: 0, quantity: 1 }],
        ...form,
      })
      navigate(`/orders`)
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Có lỗi xảy ra')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Thanh toán</h1>
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="bg-white rounded-xl p-6">
          <h2 className="font-bold mb-4">Thông tin giao hàng</h2>
          <div className="grid grid-cols-2 gap-4">
            <input className="input" placeholder="Họ và tên *" required value={form.shipping_name} onChange={e => setForm({...form, shipping_name: e.target.value})} />
            <input className="input" placeholder="Số điện thoại *" required value={form.shipping_phone} onChange={e => setForm({...form, shipping_phone: e.target.value})} />
          </div>
          <textarea className="input mt-4" placeholder="Địa chỉ *" required rows={2} value={form.shipping_address} onChange={e => setForm({...form, shipping_address: e.target.value})} />
          <input className="input mt-4" placeholder="Thành phố *" required value={form.shipping_city} onChange={e => setForm({...form, shipping_city: e.target.value})} />
          <input className="input mt-4" placeholder="Mã giảm giá (nếu có)" value={form.coupon_code} onChange={e => setForm({...form, coupon_code: e.target.value})} />
        </div>

        <div className="bg-white rounded-xl p-6">
          <h2 className="font-bold mb-4">Phương thức thanh toán</h2>
          {['cod', 'stripe', 'paypal', 'momo'].map(m => (
            <label key={m} className="flex items-center gap-3 p-3 border rounded-lg mb-2 cursor-pointer hover:bg-gray-50">
              <input type="radio" name="payment" value={m} checked={form.payment_method === m} onChange={e => setForm({...form, payment_method: e.target.value})} />
              <span className="capitalize">{m === 'cod' ? 'COD (Nhận hàng trả tiền)' : m}</span>
            </label>
          ))}
        </div>

        <div className="bg-white rounded-xl p-6">
          <h2 className="font-bold mb-4">Ghi chú</h2>
          <textarea className="input" rows={2} placeholder="Ghi chú đơn hàng (tùy chọn)" value={form.customer_note} onChange={e => setForm({...form, customer_note: e.target.value})} />
        </div>

        <div className="bg-blue-50 rounded-xl p-6">
          <div className="flex justify-between mb-2"><span>Tạm tính:</span><span>{subtotal.toLocaleString('vi-VN')}đ</span></div>
          <div className="flex justify-between mb-2"><span>Phí vận chuyển:</span><span>Tính sau</span></div>
          <div className="flex justify-between font-bold text-xl border-t pt-2 mt-2"><span>Tổng:</span><span>{subtotal.toLocaleString('vi-VN')}đ</span></div>
        </div>

        <button type="submit" disabled={loading} className="btn-primary w-full py-3 text-lg">
          {loading ? 'Đang xử lý...' : 'Đặt hàng ngay'}
        </button>
      </form>
    </div>
  )
}
