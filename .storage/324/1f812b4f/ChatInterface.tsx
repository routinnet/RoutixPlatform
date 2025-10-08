'use client'

import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { GlassCard } from '@/components/ui/GlassCard'
import { GradientButton } from '@/components/ui/GradientButton'
import { Logo } from '@/components/ui/Logo'
import { MessageBubble } from './MessageBubble'
import { ProgressIndicator } from '@/components/ui/ProgressIndicator'
import { ArrowUp, Paperclip, Image as ImageIcon, Loader2, Wifi, WifiOff } from 'lucide-react'
import { useGeneration } from '@/hooks/useGeneration'
import { useGenerationProgress } from '@/hooks/useGenerationProgress'

interface Message {
  id: string
  content: string
  type: 'user' | 'system' | 'result'
  timestamp: string
  status?: 'sending' | 'sent' | 'processing' | 'completed' | 'failed'
  generationId?: string
  result?: {
    image_url?: string
    processing_time?: number
  }
}

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  
  const { mutate: generateThumbnail, isPending } = useGeneration()
  const { 
    generations, 
    isConnected, 
    subscribeToGeneration, 
    getGenerationStatus 
  } = useGenerationProgress()

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Update messages based on real-time generation progress
  useEffect(() => {
    generations.forEach(progress => {
      setMessages(prev => prev.map(msg => {
        if (msg.generationId === progress.generation_id) {
          if (progress.status === 'completed' && progress.thumbnail_url) {
            return {
              ...msg,
              type: 'result',
              status: 'completed',
              content: 'Your thumbnail has been generated successfully! 🎉',
              result: {
                image_url: progress.thumbnail_url,
                processing_time: progress.processing_time
              }
            }
          } else if (progress.status === 'failed') {
            return {
              ...msg,
              status: 'failed',
              content: `Generation failed: ${progress.error_message || 'Unknown error'}`
            }
          } else {
            return {
              ...msg,
              status: progress.status as any,
              content: getProgressMessage(progress.status, progress.progress)
            }
          }
        }
        return msg
      }))
    })
  }, [generations])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!inputValue.trim() || isPending) return

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      content: inputValue,
      type: 'user',
      timestamp: new Date().toISOString(),
      status: 'sent'
    }

    setMessages(prev => [...prev, userMessage])
    
    const prompt = inputValue
    setInputValue('')

    // Generate thumbnail
    generateThumbnail(
      { prompt },
      {
        onSuccess: (response) => {
          const generationId = response.data.generation_id
          
          // Subscribe to real-time updates
          subscribeToGeneration(generationId)
          
          // Add processing message
          const processingMessage: Message = {
            id: `processing-${generationId}`,
            content: 'Starting thumbnail generation...',
            type: 'system',
            timestamp: new Date().toISOString(),
            status: 'processing',
            generationId
          }
          
          setMessages(prev => [...prev, processingMessage])
        }
      }
    )
  }

  const getProgressMessage = (status: string, progress: number) => {
    const messages = {
      queued: 'Your request is in queue...',
      processing: 'Generating your thumbnail with AI...',
      completed: 'Generation completed successfully!',
      failed: 'Generation failed. Please try again.'
    }
    
    return messages[status as keyof typeof messages] || `Processing... ${progress}%`
  }

  const isEmpty = messages.length === 0

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Gradient Background */}
      <div className="fixed inset-0 bg-gradient-main -z-10" />
      
      {/* Animated gradient orbs */}
      <div className="fixed inset-0 -z-10 overflow-hidden">
        <motion.div
          className="absolute w-96 h-96 bg-purple-300/30 rounded-full blur-3xl"
          animate={{
            x: [0, 100, 0],
            y: [0, -100, 0],
          }}
          transition={{ duration: 20, repeat: Infinity }}
          style={{ top: '10%', left: '20%' }}
        />
        <motion.div
          className="absolute w-96 h-96 bg-blue-300/30 rounded-full blur-3xl"
          animate={{
            x: [0, -100, 0],
            y: [0, 100, 0],
          }}
          transition={{ duration: 25, repeat: Infinity }}
          style={{ bottom: '10%', right: '20%' }}
        />
      </div>

      <div className="container max-w-4xl mx-auto px-4 py-8 flex flex-col h-screen">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between mb-8"
        >
          <GlassCard className="px-6 py-3">
            <div className="flex items-center gap-3">
              <Logo className="w-8 h-8" />
              <span className="font-bold text-text-primary text-lg">Routix</span>
              <span className="text-text-muted text-sm">AI Thumbnail Generator</span>
            </div>
          </GlassCard>

          {/* Connection Status */}
          <GlassCard className="px-4 py-2">
            <div className="flex items-center gap-2">
              {isConnected ? (
                <>
                  <Wifi className="w-4 h-4 text-green-500" />
                  <span className="text-sm text-green-600">Connected</span>
                </>
              ) : (
                <>
                  <WifiOff className="w-4 h-4 text-red-500" />
                  <span className="text-sm text-red-600">Disconnected</span>
                </>
              )}
            </div>
          </GlassCard>
        </motion.div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto mb-6 px-2">
          {isEmpty ? (
            // Welcome Screen
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="flex flex-col items-center justify-center h-full space-y-8"
            >
              {/* Logo */}
              <motion.div
                className="w-20 h-20 rounded-3xl bg-white/80 backdrop-blur-xl shadow-lg flex items-center justify-center"
                animate={{
                  scale: [1, 1.05, 1],
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
              >
                <Logo className="w-12 h-12" />
              </motion.div>

              {/* Greeting */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="text-center space-y-2"
              >
                <h1 className="text-4xl font-bold text-text-primary">
                  Hey there! 👋
                </h1>
                <h2 className="text-2xl font-semibold text-text-primary">
                  How can I help you today?
                </h2>
                <p className="text-text-secondary text-lg">
                  I'm ready to create amazing thumbnails for you
                </p>
              </motion.div>

              {/* Quick Actions */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5 }}
                className="flex justify-center gap-3 flex-wrap"
              >
                <QuickActionButton 
                  icon="🎮" 
                  label="Gaming Thumbnail" 
                  onClick={() => setInputValue('Create an epic gaming thumbnail with explosion effects')}
                />
                <QuickActionButton 
                  icon="💡" 
                  label="Tech Tutorial" 
                  onClick={() => setInputValue('Design a professional tutorial thumbnail')}
                />
                <QuickActionButton 
                  icon="🎨" 
                  label="Creative Design" 
                  onClick={() => setInputValue('Make a creative and unique thumbnail')}
                />
              </motion.div>
            </motion.div>
          ) : (
            // Messages List
            <div className="space-y-4">
              <AnimatePresence>
                {messages.map((message) => (
                  <div key={message.id}>
                    <MessageBubble message={message} />
                    
                    {/* Show progress indicator for active generations */}
                    {message.generationId && message.status === 'processing' && (
                      <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="mt-3 ml-14"
                      >
                        {(() => {
                          const progress = getGenerationStatus(message.generationId)
                          return progress ? (
                            <ProgressIndicator progress={progress} />
                          ) : null
                        })()}
                      </motion.div>
                    )}
                  </div>
                ))}
              </AnimatePresence>
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input Area */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="relative"
        >
          <form onSubmit={handleSubmit}>
            <GlassCard className="p-2">
              <div className="flex items-center gap-2">
                {/* Attachment buttons */}
                <div className="flex gap-1">
                  <button
                    type="button"
                    className="p-2 rounded-xl hover:bg-white/30 transition-colors"
                    title="Add image"
                  >
                    <ImageIcon className="w-5 h-5 text-text-muted" />
                  </button>
                  <button
                    type="button"
                    className="p-2 rounded-xl hover:bg-white/30 transition-colors"
                    title="Attach file"
                  >
                    <Paperclip className="w-5 h-5 text-text-muted" />
                  </button>
                </div>
                
                {/* Input field */}
                <input
                  ref={inputRef}
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  placeholder="Describe your thumbnail idea..."
                  className="flex-1 bg-transparent border-none outline-none px-4 py-3 text-text-primary placeholder:text-text-muted"
                  disabled={isPending}
                />
                
                {/* Send button */}
                <GradientButton
                  type="submit"
                  className="px-4 py-2 rounded-2xl"
                  disabled={!inputValue.trim() || isPending}
                >
                  {isPending ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <>
                      <span className="font-medium mr-2">Send</span>
                      <ArrowUp className="w-5 h-5" />
                    </>
                  )}
                </GradientButton>
              </div>
            </GlassCard>
          </form>
          
          {/* Input hint */}
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8 }}
            className="text-center text-text-muted text-sm mt-2"
          >
            Describe your thumbnail in detail for better results
          </motion.p>
        </motion.div>
      </div>
    </div>
  )
}

function QuickActionButton({ 
  icon, 
  label, 
  onClick 
}: { 
  icon: string
  label: string
  onClick: () => void
}) {
  return (
    <motion.button
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      onClick={onClick}
      className="group"
    >
      <GlassCard className="px-4 py-3 hover:bg-white/50 transition-all duration-200">
        <div className="flex flex-col items-center gap-2">
          <span className="text-2xl">{icon}</span>
          <span className="text-sm text-text-secondary font-medium group-hover:text-text-primary transition-colors">
            {label}
          </span>
        </div>
      </GlassCard>
    </motion.button>
  )
}