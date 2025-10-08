import { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'

export function useGenerationPolling(generationId: string) {
  const [isCompleted, setIsCompleted] = useState(false)
  
  const { data, isLoading, error } = useQuery({
    queryKey: ['generation-status', generationId],
    queryFn: () => apiClient.getGenerationStatus(generationId),
    refetchInterval: (data) => {
      // Stop polling when completed or failed
      if (data?.data?.status === 'completed' || data?.data?.status === 'failed') {
        setIsCompleted(true)
        return false
      }
      return 2000 // Poll every 2 seconds
    },
    enabled: !!generationId && !isCompleted,
  })
  
  return {
    data: data?.data,
    isLoading,
    error,
    isCompleted,
  }
}