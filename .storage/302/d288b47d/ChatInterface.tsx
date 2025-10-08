'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Loader } from 'lucide-react'
import { GlassCard } from '@/components/ui/GlassCard'
import { GradientButton } from '@/components/ui/GradientButton'
import { Logo } from '@/components/ui/Logo'
import { MessageBubble } from './MessageBubble'
import { useGeneration } from '@/hooks/useGeneration'

interface Message {
  id: string
  content: string
  type: 'user' | 'system' | 'result'
  timestamp: string
  status?: 'sending' | 'sent' | 'completed' | 'processing' | 'failed'
  progress?: number
  result?: {
    thumbnail_url: string
    title: string
  }
}

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const { mutate: generateThumbnail, isPending } = useGeneration()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isPending) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: input.trim(),
      timestamp: new Date().toISOString(),
      status: 'sent'
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')

    // Add system response
    const systemMessage: Message = {
      id: (Date.now() + 1).toString(),
      type: 'system',
      content: 'Creating your thumbnail...',
      timestamp: new Date().toISOString(),
      status: 'processing'
    }

    setMessages(prev => [...prev, systemMessage])

    // Simulate generation process
    try {
      generateThumbnail({
        prompt: input.trim(),
        algorithm_id: 'routix-v1'
      })

      // Update system message after generation
      setTimeout(() => {
        setMessages(prev => prev.map(msg => 
          msg.id === systemMessage.id 
            ? { ...msg, content: 'Your thumbnail has been generated successfully! 🎉', status: 'completed' }
            : msg
        ))
      }, 3000)
    } catch (error) {
      setMessages(prev => prev.map(msg => 
        msg.id === systemMessage.id 
          ? { ...msg, content: 'Error generating thumbnail. Please try again.', status: 'failed' }
          : msg
      ))
    }
  }

  return (
    <div className="min-h-screen bg-gradient-main">
      <div className="flex flex-col h-screen max-w-4xl mx-auto">
        {/* Header with Logo */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex justify-center py-6"
        >
          <div className="w-16 h-16 rounded-3xl bg-white/80 backdrop-blur-xl shadow-lg flex items-center justify-center">
            <Logo className="w-10 h-10" />
          </div>
        </motion.div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto px-4 pb-4">
          {messages.length === 0 ? (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="flex flex-col items-center justify-center h-full text-center space-y-6"
            >
              <div className="space-y-2">
                <h1 className="text-4xl font-bold text-text-primary">
                  Hey there! 👋
                </h1>
                <h2 className="text-3xl font-semibold text-text-primary">
                  How can I help you today?
                </h2>
                <p className="text-text-secondary text-lg">
                  I'm ready to create amazing thumbnails for you
                </p>
              </div>

              {/* Quick Actions */}
              <div className="flex flex-wrap justify-center gap-3">
                <QuickActionButton 
                  icon="🎮" 
                  label="Gaming Thumbnail" 
                  onClick={() => setInput('Create an epic gaming thumbnail')}
                />
                <QuickActionButton 
                  icon="📚" 
                  label="Tutorial Thumbnail" 
                  onClick={() => setInput('Design a professional tutorial thumbnail')}
                />
                <QuickActionButton 
                  icon="🎵" 
                  label="Music Thumbnail" 
                  onClick={() => setInput('Create a beautiful music thumbnail')}
                />
              </div>
            </motion.div>
          ) : (
            <div className="space-y-4">
              <AnimatePresence>
                {messages.map((message) => (
                  <MessageBubble key={message.id} message={message} />
                ))}
              </AnimatePresence>
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="p-4">
          <form onSubmit={handleSubmit}>
            <GlassCard className="p-3">
              <div className="flex items-center gap-3">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Describe your thumbnail idea..."
                  className="flex-1 bg-transparent border-none outline-none px-4 py-3 text-text-primary placeholder:text-text-muted"
                  disabled={isPending}
                />
                
                <GradientButton
                  type="submit"
                  className="px-6 py-3 rounded-2xl"
                  disabled={!input.trim() || isPending}
                >
                  {isPending ? (
                    <Loader className="w-5 h-5 animate-spin" />
                  ) : (
                    <>
                      <span className="font-medium mr-2">Send</span>
                      <Send className="w-5 h-5" />
                    </>
                  )}
                </GradientButton>
              </div>
            </GlassCard>
          </form>
        </div>
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
      <GlassCard className="px-4 py-3 hover:scale-105 transition-transform">
        <div className="flex flex-col items-center gap-2">
          <span className="text-2xl">{icon}</span>
          <span className="text-sm text-text-secondary font-medium">
            {label}
          </span>
        </div>
      </GlassCard>
    </motion.button>
  )
}