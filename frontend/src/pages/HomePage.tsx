import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight, Star, Truck, Shield, CreditCard } from 'lucide-react'
import api from '../api/client'

interface Product {
  id: number
  name: string
  price: number
  thumbnail_url?: string
  slug: string
  rating: number
}

export default function HomePage() {
  const [featured, setFeatured] = useState<Product[]>([])
  const [bestsellers, setBestsellers] = useState<Product[]>([])

  useEffect(() => {
    api.get('/products/featured').then(r => setFeatured(r.data)).catch(() => {})
    api.get('/products/bestsellers').then(r => setBestsellers(r.data)).catch(() => {})
  }, [])

  return (
    <div>
      {/* Hero */}
      <section className="bg-gradient-to-r from-blue-600 to-purple-600 text-white">
        <div className="max-w-7xl mx-auto px-4 py-20">
          <div className="max-w-2xl">
            <h1 className="text-4xl md:text-5xl font-bold mb-6">
              Mua sắm thông minh<br />Khám phá không giới hạn
            </h1>
            <p className="text-xl text-blue-100 mb-8">
              Hàng ngàn sản phẩm chất lượng. Thanh toán an toàn. Giao hàng nhanh chóng.
            </p>
            <div className="flex gap-4">
              <Link to="/shop" className="bg-white text-blue-600 px-6 py-3 rounded-lg font-semibold hover:bg-blue-50 transition flex items-center gap-2">
                Mua sắm ngay <ArrowRight className="w-4 h-4" />
              </Link>
              <Link to="/register" className="border border-white text-white px-6 py-3 rounded-lg font-semibold hover:bg-white/10 transition">
                Đăng ký miễn phí
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="bg-white py-12 border-b">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {[
              { icon: Truck, label: 'Miễn phí vận chuyển', desc: 'Đơn hàng từ 500K' },
              { icon: Shield, label: 'Bảo mật 100%', desc: 'Thanh toán an toàn' },
              { icon: Star, label: 'Sản phẩm chất lượng', desc: 'Được kiểm duyệt' },
              { icon: CreditCard, label: 'Nhiều hình thức', desc: 'Visa, MoMo, COD' },
            ].map(({ icon: Icon, label, desc }) => (
              <div key={label} className="flex items-center gap-3">
                <Icon className="w-8 h-8 text-blue-600 flex-shrink-0" />
                <div>
                  <div className="font-semibold text-sm">{label}</div>
                  <div className="text-xs text-gray-500">{desc}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Featured Products */}
      {featured.length > 0 && (
        <section className="py-16">
          <div className="max-w-7xl mx-auto px-4">
            <div className="flex justify-between items-center mb-8">
              <h2 className="text-2xl font-bold">Sản phẩm nổi bật</h2>
              <Link to="/shop" className="text-blue-600 hover:underline flex items-center gap-1">
                Xem tất cả <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
              {featured.map(p => (
                <Link key={p.id} to={`/product/${p.slug}`} className="card group">
                  <div className="aspect-square bg-gray-100">
                    {p.thumbnail_url ? <img src={p.thumbnail_url} alt={p.name} className="w-full h-full object-cover" /> : <div className="w-full h-full flex items-center justify-center text-gray-400">No Image</div>}
                  </div>
                  <div className="p-3">
                    <h3 className="font-medium text-sm line-clamp-2 mb-1 group-hover:text-blue-600">{p.name}</h3>
                    <div className="flex items-center gap-1 mb-2">
                      <Star className="w-3 h-3 text-yellow-400 fill-yellow-400" />
                      <span className="text-xs text-gray-500">{p.rating.toFixed(1)}</span>
                    </div>
                    <div className="font-bold text-blue-600">{p.price.toLocaleString('vi-VN')}đ</div>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Bestsellers */}
      {bestsellers.length > 0 && (
        <section className="py-16 bg-gray-50">
          <div className="max-w-7xl mx-auto px-4">
            <h2 className="text-2xl font-bold mb-8">Bán chạy nhất</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
              {bestsellers.map(p => (
                <Link key={p.id} to={`/product/${p.slug}`} className="card group">
                  <div className="aspect-square bg-gray-100">
                    {p.thumbnail_url ? <img src={p.thumbnail_url} alt={p.name} className="w-full h-full object-cover" /> : <div className="w-full h-full flex items-center justify-center text-gray-400">No Image</div>}
                  </div>
                  <div className="p-3">
                    <h3 className="font-medium text-sm line-clamp-2 mb-1 group-hover:text-blue-600">{p.name}</h3>
                    <div className="flex items-center gap-1 mb-2">
                      <Star className="w-3 h-3 text-yellow-400 fill-yellow-400" />
                      <span className="text-xs text-gray-500">{p.rating.toFixed(1)}</span>
                    </div>
                    <div className="font-bold text-blue-600">{p.price.toLocaleString('vi-VN')}đ</div>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* CTA */}
      <section className="bg-blue-600 text-white py-16">
        <div className="max-w-3xl mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-4">Bắt đầu bán hàng ngay hôm nay</h2>
          <p className="text-blue-100 mb-8">Đăng ký vendor để bắt đầu kinh doanh trên nền tảng của chúng tôi. Miễn phí đăng ký, hoa hồng thấp.</p>
          <Link to="/register" className="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-blue-50 transition">
            Trở thành người bán
          </Link>
        </div>
      </section>
    </div>
  )
}
