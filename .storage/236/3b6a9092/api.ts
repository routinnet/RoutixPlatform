import axios from 'axios'

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Redirect to login
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// API Methods
export const apiClient = {
  // Generation
  generate: (data: {
    prompt: string
    algorithm_id?: string
    user_face_url?: string
    user_logo_url?: string
    custom_text?: string
  }) =>
    api.post('/api/v1/generate', data),
  
  getGenerationStatus: (id: string) =>
    api.get(`/api/v1/generate/${id}/status`),
  
  getGenerationResult: (id: string) =>
    api.get(`/api/v1/generate/${id}/result`),
  
  getHistory: (page = 1, per_page = 20) =>
    api.get('/api/v1/generate/history', { params: { page, per_page } }),

  // Chat
  getChatHistory: (conversation_id?: string) =>
    api.get('/api/v1/chat/history', { params: { conversation_id } }),
  
  sendMessage: (data: {
    message: string
    conversation_id?: string
    message_type?: string
  }) =>
    api.post('/api/v1/chat/send', data),
}

export default api