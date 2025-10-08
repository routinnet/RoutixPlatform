import { useEffect, useState, useCallback } from 'react'
import { wsManager, GenerationProgress } from '@/lib/websocket'
import { useAuth } from '@/lib/auth'

export function useGenerationProgress() {
  const { user } = useAuth()
  const [generations, setGenerations] = useState<Map<string, GenerationProgress>>(new Map())
  const [isConnected, setIsConnected] = useState(false)

  // Connect WebSocket when user is authenticated
  useEffect(() => {
    if (user) {
      const token = localStorage.getItem('access_token')
      if (token) {
        wsManager.connect(token)
      }
    }

    return () => {
      wsManager.disconnect()
    }
  }, [user])

  // Setup event listeners
  useEffect(() => {
    const handleConnectionEstablished = () => {
      setIsConnected(true)
    }

    const handleConnectionLost = () => {
      setIsConnected(false)
    }

    const handleConnectionFailed = () => {
      setIsConnected(false)
    }

    const handleGenerationStarted = (data: GenerationProgress) => {
      setGenerations(prev => new Map(prev.set(data.generation_id, data)))
    }

    const handleGenerationProgress = (data: GenerationProgress) => {
      setGenerations(prev => new Map(prev.set(data.generation_id, data)))
    }

    const handleGenerationCompleted = (data: GenerationProgress) => {
      setGenerations(prev => new Map(prev.set(data.generation_id, data)))
    }

    const handleGenerationFailed = (data: GenerationProgress) => {
      setGenerations(prev => new Map(prev.set(data.generation_id, data)))
    }

    const handleQueueUpdate = (data: GenerationProgress) => {
      setGenerations(prev => {
        const existing = prev.get(data.generation_id)
        if (existing) {
          return new Map(prev.set(data.generation_id, { ...existing, ...data }))
        }
        return prev
      })
    }

    // Register event listeners
    wsManager.on('connection:established', handleConnectionEstablished)
    wsManager.on('connection:lost', handleConnectionLost)
    wsManager.on('connection:failed', handleConnectionFailed)
    wsManager.on('generation:started', handleGenerationStarted)
    wsManager.on('generation:progress', handleGenerationProgress)
    wsManager.on('generation:completed', handleGenerationCompleted)
    wsManager.on('generation:failed', handleGenerationFailed)
    wsManager.on('generation:queue_update', handleQueueUpdate)

    return () => {
      wsManager.off('connection:established', handleConnectionEstablished)
      wsManager.off('connection:lost', handleConnectionLost)
      wsManager.off('connection:failed', handleConnectionFailed)
      wsManager.off('generation:started', handleGenerationStarted)
      wsManager.off('generation:progress', handleGenerationProgress)
      wsManager.off('generation:completed', handleGenerationCompleted)
      wsManager.off('generation:failed', handleGenerationFailed)
      wsManager.off('generation:queue_update', handleQueueUpdate)
    }
  }, [])

  const subscribeToGeneration = useCallback((generationId: string) => {
    wsManager.subscribeToGeneration(generationId)
  }, [])

  const unsubscribeFromGeneration = useCallback((generationId: string) => {
    wsManager.unsubscribeFromGeneration(generationId)
    setGenerations(prev => {
      const newMap = new Map(prev)
      newMap.delete(generationId)
      return newMap
    })
  }, [])

  const getGenerationStatus = useCallback((generationId: string) => {
    return generations.get(generationId)
  }, [generations])

  return {
    generations: Array.from(generations.values()),
    isConnected,
    subscribeToGeneration,
    unsubscribeFromGeneration,
    getGenerationStatus,
  }
}