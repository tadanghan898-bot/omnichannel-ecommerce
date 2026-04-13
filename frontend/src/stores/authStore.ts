import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import api from '../api/client'

interface User {
  id: number
  email: string
  username?: string
  full_name?: string
  role: string
  is_active: boolean
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  register: (data: { email: string; password: string; username?: string; full_name?: string }) => Promise<void>
  logout: () => void
  checkAuth: () => Promise<void>
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,

      login: async (email, password) => {
        const res = await api.post('/api/auth/login', { email, password })
        const { access_token, user } = res.data
        api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
        set({ user, token: access_token, isAuthenticated: true })
      },

      register: async (data) => {
        const res = await api.post('/api/auth/register', data)
        const { access_token, user } = res.data
        api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
        set({ user, token: access_token, isAuthenticated: true })
      },

      logout: () => {
        delete api.defaults.headers.common['Authorization']
        set({ user: null, token: null, isAuthenticated: false })
      },

      checkAuth: async () => {
        const token = useAuthStore.getState().token
        if (token) {
          api.defaults.headers.common['Authorization'] = `Bearer ${token}`
          try {
            const res = await api.get('/api/auth/me')
            set({ user: res.data, isAuthenticated: true })
          } catch {
            useAuthStore.getState().logout()
          }
        }
      },
    }),
    { name: 'auth-storage' }
  )
)
