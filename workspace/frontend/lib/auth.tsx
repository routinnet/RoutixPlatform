'use client'

import { createContext, useContext, useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { apiClient } from './api'
import { toast } from 'sonner'

interface User {
  id: string
  username: string
  email: string
  credits: number
  role: string
}

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (username: string, password: string) => Promise<void>
  register: (data: RegisterData) => Promise<void>
  logout: () => void
  refreshUser: () => Promise<void>
}

interface RegisterData {
  username: string
  email: string
  password: string
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  // Check for existing token on mount
  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (token) {
      refreshUser()
    } else {
      setLoading(false)
    }
  }, [])

  const login = async (username: string, password: string) => {
    try {
      const { data } = await apiClient.login({ username, password })
      
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      
      await refreshUser()
      toast.success('Welcome back!')
      router.push('/chat')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Login failed')
      throw error
    }
  }

  const register = async (userData: RegisterData) => {
    try {
      await apiClient.register(userData)
      toast.success('Account created successfully! Please log in.')
      router.push('/login')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Registration failed')
      throw error
    }
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    setUser(null)
    router.push('/login')
    toast.success('Logged out successfully')
  }

  const refreshUser = async () => {
    try {
      const { data } = await apiClient.getProfile()
      setUser(data)
    } catch (error) {
      logout()
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthContext.Provider value={{
      user,
      loading,
      login,
      register,
      logout,
      refreshUser
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}

// Protected Route Component
export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!loading && !user) {
      router.push('/login')
    }
  }, [user, loading, router])

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-main flex items-center justify-center">
        <div className="w-16 h-16 rounded-3xl bg-white/80 backdrop-blur-xl shadow-lg flex items-center justify-center animate-pulse">
          <div className="w-8 h-8 bg-routix-purple/20 rounded-xl"></div>
        </div>
      </div>
    )
  }

  if (!user) {
    return null
  }

  return <>{children}</>
}