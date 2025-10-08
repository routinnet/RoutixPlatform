'use client'

import { motion } from 'framer-motion'
import { GlassCard } from '@/components/ui/GlassCard'
import { Logo } from '@/components/ui/Logo'
import { User, Bot, Loader2, CheckCircle, AlertCircle } from 'lucide-react'

interface MessageBubbleProps {
  message: {
    id: string
    content: string
    type: 'user' | 'system' | 'result'
    timestamp: string
    status?: 'sending' | 'sent' | 'processing' | 'completed' | 'failed'
    progress?: number
    result?: {
      image_url?: string
      processing_time?: number
    }
  }
  isLatest?: boolean
}

export function MessageBubble({ message, isLatest = false }: MessageBubbleProps) {
  const isUser = message.type === 'user'
  const isSystem = message.type === 'system'
  const isResult = message.type === 'result'

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex gap-4 ${isUser ? 'flex-row-reverse' : 'flex-row'} mb-6`}
    >
      {/* Avatar */}
      <div className={`flex-shrink-0 ${isUser ? 'ml-4' : 'mr-4'}`}>
        {isUser ? (
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-[#6B5DD3] to-[#8B7AFF] flex items-center justify-center">
            <User className="w-5 h-5 text-white" />
          </div>
        ) : (
          <div className="w-10 h-10 rounded-full bg-white/80 backdrop-blur-xl shadow-lg flex items-center justify-center">
            <Logo className="w-6 h-6" />
          </div>
        )}
      </div>

      {/* Message Content */}
      <div className={`flex-1 max-w-2xl ${isUser ? 'text-right' : 'text-left'}`}>
        {isUser ? (
          // User Message
          <GlassCard className="p-4 bg-gradient-to-r from-[#6B5DD3]/20 to-[#8B7AFF]/20">
            <p className="text-text-primary font-medium">{message.content}</p>
            <div className="flex items-center gap-2 mt-2">
              <span className="text-xs text-text-muted">
                {new Date(message.timestamp).toLocaleTimeString('fa-IR')}
              </span>
              {message.status === 'sending' && (
                <Loader2 className="w-3 h-3 animate-spin text-text-muted" />
              )}
              {message.status === 'sent' && (
                <CheckCircle className="w-3 h-3 text-green-500" />
              )}
            </div>
          </GlassCard>
        ) : (
          // System/Result Message
          <div className="space-y-3">
            <GlassCard className="p-6">
              {isResult && message.result?.image_url ? (
                // Result with thumbnail
                <div className="space-y-4">
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-5 h-5 text-green-500" />
                    <span className="font-semibold text-text-primary">
                      Thumbnail شما آماده است! 🎉
                    </span>
                  </div>
                  
                  <div className="rounded-2xl overflow-hidden bg-white/20 p-2">
                    <img 
                      src={message.result.image_url} 
                      alt="Generated thumbnail"
                      className="w-full h-auto rounded-xl shadow-lg"
                    />
                  </div>
                  
                  <div className="flex items-center justify-between text-sm text-text-secondary">
                    <span>زمان تولید: {message.result.processing_time}s</span>
                    <div className="flex gap-2">
                      <button className="px-3 py-1 rounded-lg bg-white/30 hover:bg-white/50 transition-colors">
                        دانلود
                      </button>
                      <button className="px-3 py-1 rounded-lg bg-white/30 hover:bg-white/50 transition-colors">
                        اشتراک‌گذاری
                      </button>
                    </div>
                  </div>
                </div>
              ) : (
                // Regular system message
                <div className="space-y-3">
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">🤖</span>
                    <h3 className="text-lg font-semibold text-text-primary">
                      Routix Intelligence
                    </h3>
                  </div>
                  
                  <p className="text-text-primary leading-relaxed">
                    {message.content}
                  </p>
                  
                  {/* Progress indicator for processing messages */}
                  {message.status === 'processing' && (
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <Loader2 className="w-4 h-4 animate-spin text-routix-purple" />
                        <span className="text-sm text-text-secondary">
                          در حال پردازش... {message.progress || 0}%
                        </span>
                      </div>
                      
                      {/* Progress bar */}
                      <div className="w-full bg-white/30 rounded-full h-2">
                        <motion.div
                          className="h-2 bg-gradient-to-r from-[#6B5DD3] to-[#8B7AFF] rounded-full"
                          initial={{ width: 0 }}
                          animate={{ width: `${message.progress || 0}%` }}
                          transition={{ duration: 0.5 }}
                        />
                      </div>
                    </div>
                  )}
                  
                  {message.status === 'failed' && (
                    <div className="flex items-center gap-2 text-red-500">
                      <AlertCircle className="w-4 h-4" />
                      <span className="text-sm">خطا در پردازش</span>
                    </div>
                  )}
                </div>
              )}
            </GlassCard>
          </div>
        )}
      </div>
    </motion.div>
  )
}