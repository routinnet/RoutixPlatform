import { useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import { toast } from 'sonner'

export function useGeneration() {
  const queryClient = useQueryClient()
  
  const mutation = useMutation({
    mutationFn: apiClient.generate,
    onSuccess: (data) => {
      toast.success('تولید thumbnail شروع شد!')
      queryClient.invalidateQueries({ queryKey: ['generations'] })
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'خطا در تولید thumbnail')
    },
  })
  
  return mutation
}