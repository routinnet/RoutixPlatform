import axios, { AxiosInstance, AxiosResponse } from 'axios'
import { toast } from 'sonner'

// API Response types
interface ApiError {
  detail?: string
  message?: string
}

interface LoginRequest {
  username: string
  password: string
}

interface RegisterRequest {
  username: string
  email: string
  password: string
}

interface AuthResponse {
  access_token: string
  refresh_token: string
  token_type: string
  user: {
    id: string
    username: string
    email: string
    credits: number
  }
}

interface GenerationRequest {
  prompt: string
  algorithm_id: string
}

interface GenerationResponse {
  id: string
  status: string
  prompt: string
  created_at: string
}

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
      timeout: 30000,
    })

    // Request interceptor to add auth token
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    })

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error)

        // Show error toast
        const errorData = error.response?.data as ApiError
        const message = errorData?.detail || errorData?.message || 'An error occurred'
        toast.error(message)

        return Promise.reject(error)
      }
    )
  }

  // Auth endpoints
  async login(data: LoginRequest): Promise<AxiosResponse<AuthResponse>> {
    return this.client.post('/users/login', data)
  }

  async register(data: RegisterRequest): Promise<AxiosResponse<AuthResponse>> {
    return this.client.post('/users/register', data)
  }

  async refreshToken(refreshToken: string): Promise<AxiosResponse<AuthResponse>> {
    return this.client.post('/users/refresh', { refresh_token: refreshToken })
  }

  // Generation endpoints
  async createGeneration(data: GenerationRequest): Promise<AxiosResponse<GenerationResponse>> {
    return this.client.post('/generations', data)
  }

  async getGeneration(id: string): Promise<AxiosResponse<GenerationResponse>> {
    return this.client.get(`/generations/${id}`)
  }

  async getUserGenerations(): Promise<AxiosResponse<GenerationResponse[]>> {
    return this.client.get('/generations/user')
  }

  // Template endpoints
  async getTemplates(): Promise<AxiosResponse<any[]>> {
    return this.client.get('/templates')
  }

  async uploadTemplate(formData: FormData): Promise<AxiosResponse<any>> {
    return this.client.post('/templates', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  }
}

export const apiClient = new ApiClient()
export type { LoginRequest, RegisterRequest, AuthResponse, GenerationRequest, GenerationResponse }