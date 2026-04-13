import { Outlet, Link, useNavigate } from 'react-router-dom'
import { ShoppingCart, User, Menu, X, Search } from 'lucide-react'
import { useState } from 'react'
import { useAuthStore } from '../stores/authStore'
import { useCartStore } from '../stores/cartStore'

export default function Layout() {
  const { user, isAuthenticated, logout } = useAuthStore()
  const { totalItems } = useCartStore()
  const navigate = useNavigate()
  const [mobileOpen, setMobileOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (searchQuery.trim()) {
      navigate(`/shop?search=${encodeURIComponent(searchQuery)}`)
    }
  }

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <Link to="/" className="text-xl font-bold text-blue-600">
              ULTIMATE Store
            </Link>

            {/* Search */}
            <form onSubmit={handleSearch} className="hidden md:flex flex-1 max-w-md mx-8">
              <div className="relative w-full">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Tìm kiếm sản phẩm..."
                  className="input pl-10"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
            </form>

            {/* Nav */}
            <nav className="flex items-center gap-4">
              <Link to="/shop" className="text-gray-600 hover:text-blue-600 transition hidden sm:block">
                Cửa hàng
              </Link>
              <Link to="/cart" className="relative text-gray-600 hover:text-blue-600 transition">
                <ShoppingCart className="w-5 h-5" />
                {totalItems > 0 && (
                  <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                    {totalItems}
                  </span>
                )}
              </Link>
              {isAuthenticated ? (
                <div className="relative group">
                  <button className="flex items-center gap-2 text-gray-600 hover:text-blue-600">
                    <User className="w-5 h-5" />
                    <span className="hidden sm:block">{user?.full_name || user?.email?.split('@')[0]}</span>
                  </button>
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border hidden group-hover:block">
                    <Link to="/account" className="block px-4 py-2 hover:bg-gray-50">Tài khoản</Link>
                    <Link to="/orders" className="block px-4 py-2 hover:bg-gray-50">Đơn hàng</Link>
                    {user?.role === 'vendor' && <Link to="/vendor" className="block px-4 py-2 hover:bg-gray-50">Kho hàng</Link>}
                    {user?.role === 'admin' && <Link to="/admin" className="block px-4 py-2 hover:bg-gray-50">Admin</Link>}
                    <button onClick={handleLogout} className="w-full text-left px-4 py-2 hover:bg-gray-50 text-red-500">Đăng xuất</button>
                  </div>
                </div>
              ) : (
                <Link to="/login" className="btn-primary text-sm">Đăng nhập</Link>
              )}
              <button className="md:hidden" onClick={() => setMobileOpen(!mobileOpen)}>
                {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
              </button>
            </nav>
          </div>
        </div>

        {/* Mobile menu */}
        {mobileOpen && (
          <div className="md:hidden bg-white border-t">
            <form onSubmit={handleSearch} className="p-4">
              <input type="text" placeholder="Tìm kiếm..." className="input" value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} />
            </form>
            <Link to="/shop" className="block px-4 py-2 hover:bg-gray-50" onClick={() => setMobileOpen(false)}>Cửa hàng</Link>
            <Link to="/cart" className="block px-4 py-2 hover:bg-gray-50" onClick={() => setMobileOpen(false)}>Giỏ hàng ({totalItems})</Link>
          </div>
        )}
      </header>

      {/* Main */}
      <main className="flex-1">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="bg-gray-900 text-white mt-16">
        <div className="max-w-7xl mx-auto px-4 py-12">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <h3 className="font-bold text-lg mb-4">ULTIMATE Store</h3>
              <p className="text-gray-400 text-sm">Nền tảng thương mại điện tử hàng đầu Việt Nam. Mua sắm thông minh, thanh toán an toàn.</p>
            </div>
            <div>
              <h4 className="font-semibold mb-3">Dịch vụ</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><Link to="/shop" className="hover:text-white">Cửa hàng</Link></li>
                <li><Link to="/orders" className="hover:text-white">Theo dõi đơn</Link></li>
                <li>Chính sách đổi trả</li>
                <li>Hỗ trợ 24/7</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-3">Thanh toán</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li>Visa / Mastercard</li>
                <li>MoMo / VNPay</li>
                <li>Chuyển khoản</li>
                <li>COD</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-3">Liên hệ</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li>Hotline: 1900-XXXX</li>
                <li>Email: support@store.com</li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-sm text-gray-500">
            ULTIMATE E-Commerce Platform v1.0 | {new Date().getFullYear()}
          </div>
        </div>
      </footer>
    </div>
  )
}
