import axios, { AxiosError } from 'axios'
import { toast } from 'sonner'

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
})

// Request interceptor (add auth token)
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor (handle errors)
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as any
    
    // Token expired - try refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      try {
        const refreshToken = localStorage.getItem('refresh_token')
        const { data } = await axios.post(
          `${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/refresh`,
          { refresh_token: refreshToken }
        )
        
        localStorage.setItem('access_token', data.access_token)
        api.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`
        
        return api(originalRequest)
      } catch (refreshError) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }
    
    // Show error toast
    const message = error.response?.data?.detail || 'An error occurred'
    toast.error(message)
    
    return Promise.reject(error)
  }
)

// API Methods
export const apiClient = {
  // Auth
  register: (data: any) => api.post('/api/v1/users/register', data),
  login: (credentials: any) => api.post('/api/v1/users/login', credentials),
  
  // User
  getProfile: () => api.get('/api/v1/users/profile'),
  updateProfile: (data: any) => api.put('/api/v1/users/profile', data),
  getCredits: () => api.get('/api/v1/users/credits'),
  
  // Chat
  getConversations: () => api.get('/api/v1/chat/conversations'),
  createConversation: () => api.post('/api/v1/chat/conversations'),
  getMessages: (id: string) => api.get(`/api/v1/chat/conversations/${id}/messages`),
  sendMessage: (id: string, message: any) => 
    api.post(`/api/v1/chat/conversations/${id}/messages`, message),
  
  // Generation
  getAlgorithms: () => api.get('/api/v1/generation/algorithms'),
  createGeneration: (data: any) => api.post('/api/v1/generation/create', data),
  getGenerationStatus: (id: string) => api.get(`/api/v1/generation/${id}/status`),
  getGenerationResult: (id: string) => api.get(`/api/v1/generation/${id}/result`),
  getHistory: () => api.get('/api/v1/generation/history'),
  
  // Templates (Admin)
  uploadTemplate: (formData: FormData) => 
    api.post('/api/v1/templates/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }),
  getTemplates: (params?: any) => api.get('/api/v1/templates', { params }),
  searchTemplates: (query: string) => 
    api.get('/api/v1/templates/search', { params: { query } }),
}

export default api