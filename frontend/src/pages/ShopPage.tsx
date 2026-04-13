import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { Star, Filter, ChevronLeft, ChevronRight } from 'lucide-react'
import api from '../api/client'

interface Product {
  id: number; name: string; price: number; thumbnail_url?: string; slug: string; rating: number; review_count: number; stock_quantity: number;
}

export default function ShopPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [pagination, setPagination] = useState({ total: 0, page: 1, pages: 1 })
  const [categories, setCategories] = useState<any[]>([])
  const [filters, setFilters] = useState({ category_id: '', brand_id: '', min_price: '', max_price: '', sort_by: 'created_at', sort_order: 'desc' })

  const page = parseInt(searchParams.get('page') || '1')
  const search = searchParams.get('search') || ''

  useEffect(() => {
    api.get('/products/categories').then(r => setCategories(r.data)).catch(() => {})
  }, [])

  useEffect(() => {
    setLoading(true)
    const params: any = { page, page_size: 20, ...filters }
    if (search) params.search = search
    Object.keys(params).forEach(k => { if (params[k] === '') delete params[k] })
    api.get('/products', { params }).then(r => {
      setProducts(r.data.items)
      setPagination({ total: r.data.total, page: r.data.page, pages: r.data.pages })
    }).catch(() => {}).finally(() => setLoading(false))
  }, [page, search, filters])

  const goPage = (p: number) => { setSearchParams(prev => { prev.set('page', String(p)); return prev }) }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">{search ? `Kết quả: "${search}"` : 'Cửa hàng'}</h1>

      {/* Filters */}
      <div className="bg-white rounded-lg p-4 mb-6 flex flex-wrap gap-4 items-center">
        <select className="input w-48" value={filters.category_id} onChange={e => setFilters({...filters, category_id: e.target.value})}>
          <option value="">Tất cả danh mục</option>
          {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
        <input type="number" placeholder="Giá từ" className="input w-32" value={filters.min_price} onChange={e => setFilters({...filters, min_price: e.target.value})} />
        <input type="number" placeholder="Giá đến" className="input w-32" value={filters.max_price} onChange={e => setFilters({...filters, max_price: e.target.value})} />
        <select className="input w-40" value={filters.sort_by} onChange={e => setFilters({...filters, sort_by: e.target.value})}>
          <option value="created_at">Mới nhất</option>
          <option value="price">Giá</option>
          <option value="rating">Đánh giá</option>
          <option value="name">Tên</option>
        </select>
        <select className="input w-32" value={filters.sort_order} onChange={e => setFilters({...filters, sort_order: e.target.value})}>
          <option value="desc">Giảm dần</option>
          <option value="asc">Tăng dần</option>
        </select>
      </div>

      {/* Products */}
      {loading ? (
        <div className="text-center py-20 text-gray-500">Đang tải...</div>
      ) : products.length === 0 ? (
        <div className="text-center py-20 text-gray-500">Không tìm thấy sản phẩm nào</div>
      ) : (
        <>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4 mb-8">
            {products.map(p => (
              <Link key={p.id} to={`/product/${p.slug}`} className="card group">
                <div className="aspect-square bg-gray-100">
                  {p.thumbnail_url ? <img src={p.thumbnail_url} alt={p.name} className="w-full h-full object-cover" /> : <div className="w-full h-full flex items-center justify-center text-gray-400 text-sm">No Image</div>}
                </div>
                <div className="p-3">
                  <h3 className="font-medium text-sm line-clamp-2 mb-1 group-hover:text-blue-600">{p.name}</h3>
                  <div className="flex items-center gap-1 mb-2">
                    <Star className="w-3 h-3 text-yellow-400 fill-yellow-400" />
                    <span className="text-xs text-gray-500">{p.rating.toFixed(1)} ({p.review_count})</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-blue-600">{p.price.toLocaleString('vi-VN')}đ</span>
                    {p.stock_quantity === 0 && <span className="text-xs text-red-500">Hết hàng</span>}
                  </div>
                </div>
              </Link>
            ))}
          </div>

          {/* Pagination */}
          {pagination.pages > 1 && (
            <div className="flex justify-center items-center gap-2">
              <button disabled={page <= 1} onClick={() => goPage(page - 1)} className="p-2 rounded hover:bg-gray-200 disabled:opacity-50"><ChevronLeft className="w-5 h-5" /></button>
              {Array.from({length: Math.min(pagination.pages, 10)}, (_, i) => i + 1).map(p => (
                <button key={p} onClick={() => goPage(p)} className={`w-8 h-8 rounded ${p === page ? 'bg-blue-600 text-white' : 'hover:bg-gray-200'}`}>{p}</button>
              ))}
              <button disabled={page >= pagination.pages} onClick={() => goPage(page + 1)} className="p-2 rounded hover:bg-gray-200 disabled:opacity-50"><ChevronRight className="w-5 h-5" /></button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
