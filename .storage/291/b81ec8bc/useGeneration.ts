import { useMutation } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import { toast } from 'sonner'

interface GenerationRequest {
  prompt: string
  algorithm_id: string
}

export function useGeneration() {
  return useMutation({
    mutationFn: async (data: GenerationRequest) => {
      const response = await apiClient.createGeneration(data)
      return response.data
    },
    onSuccess: (data) => {
      toast.success('Generation started successfully!')
    },
    onError: (error) => {
      toast.error('Failed to start generation')
      console.error('Generation error:', error)
    },
  })
}