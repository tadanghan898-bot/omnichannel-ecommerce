import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Star, ShoppingCart, Heart, Minus, Plus } from 'lucide-react'
import api from '../api/client'
import { useCartStore } from '../stores/cartStore'
import { useAuthStore } from '../stores/authStore'

interface Product {
  id: number; name: string; price: number; description?: string; short_description?: string
  thumbnail_url?: string; images: any[]; rating: number; review_count: number; stock_quantity: number
  category_id?: number; tags: string[]; slug: string
}

interface Review {
  id: number; rating: number; title?: string; comment?: string; user_name?: string; created_at: string
}

export default function ProductPage() {
  const { slug } = useParams()
  const [product, setProduct] = useState<Product | null>(null)
  const [reviews, setReviews] = useState<Review[]>([])
  const [quantity, setQuantity] = useState(1)
  const [loading, setLoading] = useState(true)
  const { addToCart } = useCartStore()
  const { isAuthenticated } = useAuthStore()

  useEffect(() => {
    if (!slug) return
    api.get(`/products/slug/${slug}`).then(r => setProduct(r.data)).catch(() => {}).finally(() => setLoading(false))
    api.get(`/products/${slug}/reviews`).then(r => setReviews(r.data)).catch(() => {})
  }, [slug])

  if (loading) return <div className="text-center py-20">Đang tải...</div>
  if (!product) return <div className="text-center py-20">Không tìm thấy sản phẩm</div>

  const images = product.images?.length ? product.images : (product.thumbnail_url ? [{ url: product.thumbnail_url }] : [])

  const handleAddToCart = async () => {
    if (!isAuthenticated) { window.location.href = '/login'; return }
    await addToCart(product.id, quantity)
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="grid md:grid-cols-2 gap-8 mb-12">
        {/* Images */}
        <div>
          <div className="aspect-square bg-gray-100 rounded-xl overflow-hidden mb-4">
            {images[0] ? <img src={images[0].url} alt={product.name} className="w-full h-full object-cover" /> : <div className="w-full h-full flex items-center justify-center text-gray-400">No Image</div>}
          </div>
          {images.length > 1 && (
            <div className="flex gap-2 overflow-x-auto">
              {images.map((img: any, i: number) => (
                <div key={i} className="w-20 h-20 flex-shrink-0 rounded-lg overflow-hidden border">
                  <img src={img.url} alt="" className="w-full h-full object-cover" />
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Info */}
        <div>
          <h1 className="text-2xl font-bold mb-2">{product.name}</h1>
          <div className="flex items-center gap-2 mb-4">
            <div className="flex items-center gap-1">
              {[1,2,3,4,5].map(s => <Star key={s} className={`w-4 h-4 ${s <= product.rating ? 'text-yellow-400 fill-yellow-400' : 'text-gray-300'}`} />)}
            </div>
            <span className="text-sm text-gray-500">{product.rating.toFixed(1)} ({product.review_count} đánh giá)</span>
          </div>

          <div className="text-3xl font-bold text-blue-600 mb-6">{product.price.toLocaleString('vi-VN')}đ</div>

          <p className="text-gray-600 mb-6">{product.short_description || product.description?.substring(0, 200)}</p>

          {/* Stock */}
          <div className="mb-6">
            {product.stock_quantity > 0 ? (
              <span className="text-green-600 text-sm font-medium">Còn hàng ({product.stock_quantity})</span>
            ) : (
              <span className="text-red-500 text-sm font-medium">Hết hàng</span>
            )}
          </div>

          {/* Quantity */}
          <div className="flex items-center gap-4 mb-6">
            <span className="text-sm text-gray-600">Số lượng:</span>
            <div className="flex items-center border rounded-lg">
              <button onClick={() => setQuantity(Math.max(1, quantity - 1))} className="p-2 hover:bg-gray-100"><Minus className="w-4 h-4" /></button>
              <input type="number" value={quantity} min={1} max={product.stock_quantity} onChange={e => setQuantity(Math.max(1, parseInt(e.target.value) || 1))} className="w-16 text-center border-x py-2 outline-none" />
              <button onClick={() => setQuantity(Math.min(product.stock_quantity, quantity + 1))} className="p-2 hover:bg-gray-100"><Plus className="w-4 h-4" /></button>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-3 mb-6">
            <button onClick={handleAddToCart} disabled={product.stock_quantity === 0} className="btn-primary flex items-center gap-2 flex-1 justify-center">
              <ShoppingCart className="w-5 h-5" /> Thêm vào giỏ
            </button>
            <button className="btn-secondary flex items-center gap-2 px-4"><Heart className="w-5 h-5" /></button>
          </div>

          {/* Tags */}
          {product.tags?.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {product.tags.map((tag: string) => (
                <span key={tag} className="px-2 py-1 bg-gray-100 rounded text-xs">{tag}</span>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Description */}
      {product.description && (
        <div className="bg-white rounded-xl p-6 mb-8">
          <h2 className="text-xl font-bold mb-4">Mô tả sản phẩm</h2>
          <div className="prose max-w-none text-gray-600 whitespace-pre-wrap">{product.description}</div>
        </div>
      )}

      {/* Reviews */}
      <div className="bg-white rounded-xl p-6">
        <h2 className="text-xl font-bold mb-4">Đánh giá sản phẩm</h2>
        {reviews.length === 0 ? (
          <p className="text-gray-500">Chưa có đánh giá nào</p>
        ) : (
          <div className="space-y-4">
            {reviews.map(r => (
              <div key={r.id} className="border-b pb-4">
                <div className="flex items-center gap-2 mb-2">
                  <div className="flex">{[1,2,3,4,5].map(s => <Star key={s} className={`w-3 h-3 ${s <= r.rating ? 'text-yellow-400 fill-yellow-400' : 'text-gray-300'}`} />)}</div>
                  <span className="font-medium text-sm">{r.user_name || 'Anonymous'}</span>
                  <span className="text-xs text-gray-400">{new Date(r.created_at).toLocaleDateString('vi-VN')}</span>
                </div>
                {r.title && <div className="font-medium mb-1">{r.title}</div>}
                {r.comment && <p className="text-gray-600 text-sm">{r.comment}</p>}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
