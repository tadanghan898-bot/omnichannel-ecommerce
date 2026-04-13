import { create } from 'zustand'
import api from '../api/client'

interface CartItem {
  id: number
  product_id: number
  quantity: number
  product_name: string
  product_image?: string
  product_price: number
  product_slug: string
  subtotal: number
}

interface CartState {
  items: CartItem[]
  totalItems: number
  subtotal: number
  loading: boolean
  fetchCart: () => Promise<void>
  addToCart: (productId: number, quantity?: number) => Promise<void>
  updateItem: (itemId: number, quantity: number) => Promise<void>
  removeItem: (itemId: number) => Promise<void>
  clearCart: () => Promise<void>
}

export const useCartStore = create<CartState>((set) => ({
  items: [],
  totalItems: 0,
  subtotal: 0,
  loading: false,

  fetchCart: async () => {
    set({ loading: true })
    try {
      const res = await api.get('/api/cart')
      set({ items: res.data.items || [], totalItems: res.data.total_items || 0, subtotal: res.data.subtotal || 0 })
    } catch {
      // Not logged in or cart empty
    }
    set({ loading: false })
  },

  addToCart: async (productId, quantity = 1) => {
    await api.post('/api/cart/items', { product_id: productId, quantity })
    await useCartStore.getState().fetchCart()
  },

  updateItem: async (itemId, quantity) => {
    await api.put(`/api/cart/items/${itemId}`, { quantity })
    await useCartStore.getState().fetchCart()
  },

  removeItem: async (itemId) => {
    await api.delete(`/api/cart/items/${itemId}`)
    await useCartStore.getState().fetchCart()
  },

  clearCart: async () => {
    await api.delete('/api/cart')
    set({ items: [], totalItems: 0, subtotal: 0 })
  },
}))
