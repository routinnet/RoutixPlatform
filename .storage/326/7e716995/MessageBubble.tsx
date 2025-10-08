'use client'

import { motion } from 'framer-motion'
import { User, Bot, CheckCircle, Clock, AlertCircle } from 'lucide-react'
import { GlassCard } from '@/components/ui/GlassCard'

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

interface MessageBubbleProps {
  message: Message
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.type === 'user'
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
    >
      {/* Avatar */}
      <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${
        isUser 
          ? 'bg-gradient-purple text-white' 
          : 'bg-white/80 backdrop-blur-xl text-text-primary'
      }`}>
        {isUser ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
      </div>
      
      {/* Message */}
      <div className={`max-w-[70%] ${isUser ? 'text-right' : 'text-left'}`}>
        <GlassCard className={`p-4 ${isUser ? 'bg-gradient-purple text-white' : ''}`}>
          <p className="text-sm leading-relaxed">{message.content}</p>
          
          {/* Status indicator */}
          {message.status && (
            <div className="flex items-center gap-2 mt-2 text-xs opacity-70">
              {message.status === 'sending' && <Clock className="w-3 h-3" />}
              {message.status === 'sent' && <CheckCircle className="w-3 h-3" />}
              {message.status === 'processing' && <Clock className="w-3 h-3 animate-spin" />}
              {message.status === 'completed' && <CheckCircle className="w-3 h-3" />}
              {message.status === 'failed' && <AlertCircle className="w-3 h-3" />}
              <span>{message.status}</span>
            </div>
          )}
          
          {/* Progress bar */}
          {message.progress !== undefined && (
            <div className="mt-3">
              <div className="w-full bg-white/20 rounded-full h-2">
                <div 
                  className="bg-white h-2 rounded-full transition-all duration-300"
                  style={{ width: `${message.progress}%` }}
                />
              </div>
              <p className="text-xs mt-1 opacity-70">{message.progress}% complete</p>
            </div>
          )}
          
          {/* Result thumbnail */}
          {message.result && (
            <div className="mt-3">
              <img 
                src={message.result.thumbnail_url} 
                alt={message.result.title}
                className="rounded-xl max-w-full h-auto"
              />
              <p className="text-xs mt-2 opacity-70">{message.result.title}</p>
            </div>
          )}
        </GlassCard>
        
        {/* Timestamp */}
        <p className="text-xs text-text-muted mt-1 px-2">
          {new Date(message.timestamp).toLocaleTimeString()}
        </p>
      </div>
    </motion.div>
  )
}