import { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'

export function useGenerationPolling(generationId: string) {
  const [isCompleted, setIsCompleted] = useState(false)
  
  const { data, isLoading, error } = useQuery({
    queryKey: ['generation-status', generationId],
    queryFn: () => apiClient.getGenerationStatus(generationId),
    refetchInterval: (query) => {
      // Stop polling when completed or failed
      const responseData = query.state.data
      if (responseData?.data?.status === 'completed' || responseData?.data?.status === 'failed') {
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