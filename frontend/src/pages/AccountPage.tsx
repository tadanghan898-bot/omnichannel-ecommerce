import { useEffect, useState } from 'react'
import { useAuthStore } from '../stores/authStore'
import api from '../api/client'

export default function AccountPage() {
  const { user } = useAuthStore()
  const [profile, setProfile] = useState<any>(null)
  const [editMode, setEditMode] = useState(false)
  const [form, setForm] = useState({ full_name: '', phone: '' })

  useEffect(() => {
    api.get('/api/auth/me').then(r => { setProfile(r.data); setForm({ full_name: r.data.full_name || '', phone: r.data.phone || '' }) }).catch(() => {})
  }, [])

  const handleSave = async () => {
    try {
      const r = await api.put('/api/auth/me', form)
      setProfile(r.data)
      setEditMode(false)
    } catch {}
  }

  if (!profile) return <div className="text-center py-20">Đang tải...</div>

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Tài khoản của tôi</h1>
      <div className="bg-white rounded-xl p-6 mb-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="font-bold">Thông tin cá nhân</h2>
          <button onClick={() => setEditMode(!editMode)} className="text-blue-600 text-sm">{editMode ? 'Hủy' : 'Chỉnh sửa'}</button>
        </div>
        {editMode ? (
          <div className="space-y-4">
            <input className="input" placeholder="Họ và tên" value={form.full_name} onChange={e => setForm({...form, full_name: e.target.value})} />
            <input className="input" placeholder="Số điện thoại" value={form.phone} onChange={e => setForm({...form, phone: e.target.value})} />
            <button onClick={handleSave} className="btn-primary">Lưu thay đổi</button>
          </div>
        ) : (
          <div className="space-y-2 text-sm">
            <div><span className="text-gray-500">Email:</span> {profile.email}</div>
            <div><span className="text-gray-500">Họ tên:</span> {profile.full_name || 'Chưa cập nhật'}</div>
            <div><span className="text-gray-500">SĐT:</span> {profile.phone || 'Chưa cập nhật'}</div>
            <div><span className="text-gray-500">Vai trò:</span> <span className="capitalize">{profile.role}</span></div>
          </div>
        )}
      </div>
    </div>
  )
}
