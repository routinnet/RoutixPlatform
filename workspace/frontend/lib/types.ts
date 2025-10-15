/**
 * API Type Definitions for Routix Platform
 */

export interface RegisterData {
  username: string
  email: string
  password: string
  full_name?: string
  referral_code?: string
}

export interface LoginCredentials {
  username_or_email: string
  password: string
  remember_me?: boolean
}

export interface UpdateProfileData {
  full_name?: string
  email?: string
  bio?: string
  website?: string
  location?: string
  avatar_url?: string
  preferences?: Record<string, unknown>
}

export interface SendMessageData {
  content: string
  metadata?: Record<string, unknown>
}

export interface CreateGenerationData {
  prompt: string
  template_id?: string
  user_face_url?: string
  user_logo_url?: string
  custom_text?: string
  algorithm?: string
  parameters?: Record<string, unknown>
}

export interface GenerationHistoryParams {
  limit?: number
  offset?: number
  status?: string
  sort_by?: string
}

export interface TemplateQueryParams {
  limit?: number
  offset?: number
  category?: string
  tags?: string[]
  search?: string
}

export interface UpdateTemplateData {
  name?: string
  description?: string
  category?: string
  tags?: string[]
  is_public?: boolean
  metadata?: Record<string, unknown>
}

export interface ShareGenerationData {
  platform?: string
  message?: string
  recipients?: string[]
}

export interface AdminUserParams {
  limit?: number
  offset?: number
  role?: string
  status?: string
  search?: string
}

export interface UpdateUserData {
  role?: string
  is_active?: boolean
  credits?: number
  subscription_tier?: string
}

export interface AnalyticsParams {
  start_date?: string
  end_date?: string
  metric?: string
  granularity?: string
}
