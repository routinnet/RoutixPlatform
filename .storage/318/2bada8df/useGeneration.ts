import { useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import { toast } from 'sonner'

export function useGeneration() {
  const queryClient = useQueryClient()
  
  const mutation = useMutation({
    mutationFn: apiClient.createGeneration,
    onSuccess: (data) => {
      toast.success('Thumbnail generation started!')
      queryClient.invalidateQueries({ queryKey: ['generations'] })
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to start generation')
    },
  })
  
  return mutation
}