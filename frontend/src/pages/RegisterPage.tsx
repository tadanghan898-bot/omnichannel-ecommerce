import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'

export default function RegisterPage() {
  const { register } = useAuthStore()
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', password: '', username: '', full_name: '' })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      await register(form)
      navigate('/')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Đăng ký thất bại')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-[calc(100vh-200px)] flex items-center justify-center px-4 py-8">
      <div className="bg-white rounded-xl shadow-lg p-8 w-full max-w-md">
        <h1 className="text-2xl font-bold text-center mb-6">Đăng ký tài khoản</h1>
        {error && <div className="bg-red-50 text-red-600 p-3 rounded-lg mb-4 text-sm">{error}</div>}
        <form onSubmit={handleSubmit} className="space-y-4">
          <input type="text" className="input" placeholder="Họ và tên" value={form.full_name} onChange={e => setForm({...form, full_name: e.target.value})} />
          <input type="text" className="input" placeholder="Tên đăng nhập" value={form.username} onChange={e => setForm({...form, username: e.target.value})} />
          <input type="email" className="input" placeholder="Email *" required value={form.email} onChange={e => setForm({...form, email: e.target.value})} />
          <input type="password" className="input" placeholder="Mật khẩu *" required value={form.password} onChange={e => setForm({...form, password: e.target.value})} />
          <button type="submit" disabled={loading} className="btn-primary w-full py-3">{loading ? 'Đang đăng ký...' : 'Đăng ký'}</button>
        </form>
        <p className="text-center text-sm text-gray-500 mt-4">
          Đã có tài khoản? <Link to="/login" className="text-blue-600 hover:underline">Đăng nhập</Link>
        </p>
      </div>
    </div>
  )
}
