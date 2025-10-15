import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'
import { toast } from 'sonner'
import type {
  RegisterData,
  LoginCredentials,
  UpdateProfileData,
  SendMessageData,
  CreateGenerationData,
  GenerationHistoryParams,
  TemplateQueryParams,
  UpdateTemplateData,
  ShareGenerationData,
  AdminUserParams,
  UpdateUserData,
  AnalyticsParams,
} from './types'

const FALLBACK_API_URL = 'http://localhost:8000'
const LOGIN_ROUTE = '/login'
const REFRESH_ROUTE = '/api/v1/auth/refresh'
const REQUEST_TIMEOUT = 30_000
const isBrowser = typeof window !== 'undefined'

type RefreshResponse = {
  access_token: string
}

const resolveBaseUrl = (): string => {
  const envUrl = process.env.NEXT_PUBLIC_API_URL?.trim()
  if (envUrl) {
    return envUrl.replace(/\/$/, '')
  }

  if (isBrowser) {
    const { protocol, hostname, port } = window.location
    const isLocalhost = hostname === 'localhost' || hostname === '127.0.0.1'
    const effectivePort = isLocalhost ? '8000' : port
    const portSegment = effectivePort ? `:${effectivePort}` : ''
    return `${protocol}//${hostname}${portSegment}`
  }

  return FALLBACK_API_URL
}

const getStoredToken = (key: 'access_token' | 'refresh_token'): string | null => {
  if (!isBrowser) return null
  return window.localStorage.getItem(key)
}

const persistAccessToken = (token: string): void => {
  if (!isBrowser) return
  window.localStorage.setItem('access_token', token)
}

const clearStoredTokens = (): void => {
  if (!isBrowser) return
  window.localStorage.removeItem('access_token')
  window.localStorage.removeItem('refresh_token')
}

const redirectToLogin = (): void => {
  if (!isBrowser) return
  window.location.href = LOGIN_ROUTE
}

const api = axios.create({
  baseURL: resolveBaseUrl(),
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: REQUEST_TIMEOUT,
})

let refreshTokenPromise: Promise<string | null> | null = null

const attachAccessToken = (config: InternalAxiosRequestConfig): InternalAxiosRequestConfig => {
  const token = getStoredToken('access_token')
  if (token) {
    config.headers = config.headers ?? {}
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
}

api.interceptors.request.use(attachAccessToken, (error) => Promise.reject(error))

const refreshAccessToken = async (): Promise<string | null> => {
  if (!isBrowser) return null

  const refreshToken = getStoredToken('refresh_token')
  if (!refreshToken) {
    clearStoredTokens()
    redirectToLogin()
    return null
  }

  const { data } = await api.post<RefreshResponse>(REFRESH_ROUTE, {
    refresh_token: refreshToken,
  })

  persistAccessToken(data.access_token)
  api.defaults.headers.common.Authorization = `Bearer ${data.access_token}`
  return data.access_token
}

const handleUnauthorized = async (
  error: AxiosError,
  originalRequest: InternalAxiosRequestConfig & { _retry?: boolean }
) => {
  if (originalRequest._retry) {
    clearStoredTokens()
    redirectToLogin()
    return Promise.reject(error)
  }

  originalRequest._retry = true

  try {
    refreshTokenPromise = refreshTokenPromise ?? refreshAccessToken()
    const newAccessToken = await refreshTokenPromise
    refreshTokenPromise = null

    if (!newAccessToken) {
      return Promise.reject(error)
    }

    originalRequest.headers = {
      ...(originalRequest.headers ?? {}),
      Authorization: `Bearer ${newAccessToken}`,
    }

    return api(originalRequest)
  } catch (refreshError) {
    clearStoredTokens()
    redirectToLogin()
    return Promise.reject(refreshError)
  }
}

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = (error.config || {}) as InternalAxiosRequestConfig & {
      _retry?: boolean
    }

    if (error.response?.status === 401 && isBrowser) {
      return handleUnauthorized(error, originalRequest)
    }

    if (isBrowser) {
      const message =
        (error.response?.data as { detail?: string })?.detail ||
        (error.message?.includes('Network Error')
          ? 'Network error. Please check your connection and try again.'
          : error.message || 'An unexpected error occurred')
      toast.error(message)
    }

    return Promise.reject(error)
  }
)

// API Methods
export const apiClient = {
  // Auth
  register: (data: RegisterData) => api.post('/api/v1/users/register', data),
  login: (credentials: LoginCredentials) => api.post('/api/v1/users/login', credentials),
  
  // User
  getProfile: () => api.get('/api/v1/users/profile'),
  updateProfile: (data: UpdateProfileData) => api.put('/api/v1/users/profile', data),
  getCredits: () => api.get('/api/v1/users/credits'),
  
  // Chat
  getConversations: () => api.get('/api/v1/chat/conversations'),
  createConversation: () => api.post('/api/v1/chat/conversations'),
  getMessages: (id: string) => api.get(`/api/v1/chat/conversations/${id}/messages`),
  sendMessage: (id: string, message: SendMessageData) => 
    api.post(`/api/v1/chat/conversations/${id}/messages`, message),
  
  // Generation
  getAlgorithms: () => api.get('/api/v1/generation/algorithms'),
  createGeneration: (data: CreateGenerationData) => api.post('/api/v1/generation/create', data),
  getGenerationStatus: (id: string) => api.get(`/api/v1/generation/${id}/status`),
  getGenerationResult: (id: string) => api.get(`/api/v1/generation/${id}/result`),
  getHistory: (params?: GenerationHistoryParams) => api.get('/api/v1/generations/user', { params }),
  
  // Templates
  uploadTemplate: (formData: FormData) =>
    api.post('/api/v1/templates/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  getTemplates: (params?: TemplateQueryParams) => api.get('/api/v1/templates', { params }),
  searchTemplates: (query: string) => 
    api.get('/api/v1/templates/search', { params: { query } }),
  deleteTemplate: (id: string) => api.delete(`/api/v1/templates/${id}`),
  updateTemplate: (id: string, data: UpdateTemplateData) => api.put(`/api/v1/templates/${id}`, data),
  
  // Gallery & History
  downloadGeneration: (id: string) => api.get(`/api/v1/generations/${id}/download`, {
    responseType: 'blob'
  }),
  shareGeneration: (id: string, data: ShareGenerationData) => api.post(`/api/v1/generations/${id}/share`, data),
  favoriteGeneration: (id: string) => api.post(`/api/v1/generations/${id}/favorite`),
  unfavoriteGeneration: (id: string) => api.delete(`/api/v1/generations/${id}/favorite`),
  deleteGeneration: (id: string) => api.delete(`/api/v1/generations/${id}`),
  
  // Admin APIs
  getAdminStats: () => api.get('/api/v1/admin/stats'),
  getUsers: (params?: AdminUserParams) => api.get('/api/v1/admin/users', { params }),
  updateUser: (id: string, data: UpdateUserData) => api.put(`/api/v1/admin/users/${id}`, data),
  getAnalytics: (params?: AnalyticsParams) => api.get('/api/v1/admin/analytics', { params }),
  getRecentActivity: () => api.get('/api/v1/admin/activity'),
}

export default api
