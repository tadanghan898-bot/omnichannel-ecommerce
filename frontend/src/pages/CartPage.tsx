import { useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Minus, Plus, Trash2, ShoppingBag } from 'lucide-react'
import { useCartStore } from '../stores/cartStore'
import { useAuthStore } from '../stores/authStore'

export default function CartPage() {
  const { items, totalItems, subtotal, fetchCart, updateItem, removeItem, clearCart } = useCartStore()
  const { isAuthenticated } = useAuthStore()

  useEffect(() => { fetchCart() }, [])

  if (!isAuthenticated) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center">
        <ShoppingBag className="w-16 h-16 text-gray-300 mx-auto mb-4" />
        <h2 className="text-xl font-bold mb-2">Giỏ hàng trống</h2>
        <p className="text-gray-500 mb-6">Vui lòng đăng nhập để xem giỏ hàng</p>
        <Link to="/login" className="btn-primary">Đăng nhập</Link>
      </div>
    )
  }

  if (items.length === 0) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center">
        <ShoppingBag className="w-16 h-16 text-gray-300 mx-auto mb-4" />
        <h2 className="text-xl font-bold mb-2">Giỏ hàng trống</h2>
        <p className="text-gray-500 mb-6">Hãy thêm sản phẩm vào giỏ hàng</p>
        <Link to="/shop" className="btn-primary">Tiếp tục mua sắm</Link>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Giỏ hàng ({totalItems} sản phẩm)</h1>

      <div className="space-y-4">
        {items.map(item => (
          <div key={item.id} className="bg-white rounded-xl p-4 flex gap-4">
            <Link to={`/product/${item.product_slug}`} className="w-24 h-24 bg-gray-100 rounded-lg flex-shrink-0 overflow-hidden">
              {item.product_image ? <img src={item.product_image} alt={item.product_name} className="w-full h-full object-cover" /> : <div className="w-full h-full flex items-center justify-center text-gray-400 text-xs">No Img</div>}
            </Link>
            <div className="flex-1 min-w-0">
              <Link to={`/product/${item.product_slug}`} className="font-medium hover:text-blue-600 line-clamp-2">{item.product_name}</Link>
              <div className="font-bold text-blue-600 mt-1">{item.product_price.toLocaleString('vi-VN')}đ</div>
            </div>
            <div className="flex flex-col items-end justify-between">
              <button onClick={() => removeItem(item.id)} className="text-gray-400 hover:text-red-500"><Trash2 className="w-4 h-4" /></button>
              <div className="flex items-center border rounded-lg">
                <button onClick={() => updateItem(item.id, Math.max(1, item.quantity - 1))} className="p-1 hover:bg-gray-100"><Minus className="w-4 h-4" /></button>
                <span className="w-8 text-center text-sm">{item.quantity}</span>
                <button onClick={() => updateItem(item.id, item.quantity + 1)} className="p-1 hover:bg-gray-100"><Plus className="w-4 h-4" /></button>
              </div>
              <div className="font-bold">{item.subtotal.toLocaleString('vi-VN')}đ</div>
            </div>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-xl p-6 mt-6">
        <div className="flex justify-between items-center mb-4">
          <span className="text-gray-600">Tạm tính:</span>
          <span className="font-bold text-lg">{subtotal.toLocaleString('vi-VN')}đ</span>
        </div>
        <div className="flex justify-between items-center mb-6">
          <span className="text-gray-600">Tổng cộng:</span>
          <span className="font-bold text-2xl text-blue-600">{subtotal.toLocaleString('vi-VN')}đ</span>
        </div>
        <Link to="/checkout" className="btn-primary w-full text-center block">Tiến hành thanh toán</Link>
      </div>
    </div>
  )
}
