import { create } from 'zustand'

interface AuthState {
  isAuthenticated: boolean
  user: any | null
  token: string | null
  login: (token: string, user: any) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  isAuthenticated: !!localStorage.getItem('token'),
  user: null,
  token: localStorage.getItem('token'),
  
  login: (token: string, user: any) => {
    localStorage.setItem('token', token)
    set({ isAuthenticated: true, token, user })
  },
  
  logout: () => {
    localStorage.removeItem('token')
    set({ isAuthenticated: false, token: null, user: null })
  },
}))
