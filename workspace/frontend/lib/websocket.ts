import { io, Socket } from 'socket.io-client'

export interface GenerationProgress {
  generation_id: string
  status: 'queued' | 'processing' | 'completed' | 'failed'
  progress: number
  queue_position?: number
  estimated_time?: number
  error_message?: string
  thumbnail_url?: string
  processing_time?: number
}

class WebSocketManager {
  private socket: Socket | null = null
  private listeners: Map<string, Set<Function>> = new Map()
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000

  connect(token: string) {
    if (this.socket?.connected) return

    this.socket = io(process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000', {
      auth: { token },
      transports: ['websocket'],
      reconnection: true,
      reconnectionAttempts: this.maxReconnectAttempts,
      reconnectionDelay: this.reconnectDelay,
    })

    this.setupEventHandlers()
  }

  private setupEventHandlers() {
    if (!this.socket) return

    this.socket.on('connect', () => {
      console.log('✅ WebSocket connected')
      this.reconnectAttempts = 0
      this.emit('connection:established', { connected: true })
    })

    this.socket.on('disconnect', (reason) => {
      console.log('❌ WebSocket disconnected:', reason)
      this.emit('connection:lost', { reason })
    })

    this.socket.on('connect_error', (error) => {
      console.error('❌ WebSocket connection error:', error)
      this.reconnectAttempts++
      
      if (this.reconnectAttempts >= this.maxReconnectAttempts) {
        this.emit('connection:failed', { error })
      }
    })

    // Generation events
    this.socket.on('generation_started', (data: GenerationProgress) => {
      console.log('🚀 Generation started:', data)
      this.emit('generation:started', data)
    })

    this.socket.on('generation_progress', (data: GenerationProgress) => {
      console.log('📊 Generation progress:', data)
      this.emit('generation:progress', data)
    })

    this.socket.on('generation_completed', (data: GenerationProgress) => {
      console.log('✅ Generation completed:', data)
      this.emit('generation:completed', data)
    })

    this.socket.on('generation_failed', (data: GenerationProgress) => {
      console.log('❌ Generation failed:', data)
      this.emit('generation:failed', data)
    })

    this.socket.on('queue_position', (data: GenerationProgress) => {
      console.log('📍 Queue position updated:', data)
      this.emit('generation:queue_update', data)
    })
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
    }
    this.listeners.clear()
  }

  // Subscribe to generation updates for specific ID
  subscribeToGeneration(generationId: string) {
    if (this.socket?.connected) {
      this.socket.emit('subscribe_generation', { generation_id: generationId })
    }
  }

  // Unsubscribe from generation updates
  unsubscribeFromGeneration(generationId: string) {
    if (this.socket?.connected) {
      this.socket.emit('unsubscribe_generation', { generation_id: generationId })
    }
  }

  // Event listener management
  on(event: string, callback: Function) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set())
    }
    this.listeners.get(event)!.add(callback)
  }

  off(event: string, callback: Function) {
    this.listeners.get(event)?.delete(callback)
  }

  private emit(event: string, data: unknown) {
    this.listeners.get(event)?.forEach(callback => {
      try {
        callback(data)
      } catch (error) {
        console.error('Error in WebSocket event callback:', error)
      }
    })
  }

  // Connection status
  get isConnected() {
    return this.socket?.connected || false
  }

  get connectionId() {
    return this.socket?.id
  }
}

export const wsManager = new WebSocketManager()
