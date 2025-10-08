'use client'

import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { GlassCard } from '@/components/ui/GlassCard'
import { GradientButton } from '@/components/ui/GradientButton'
import { Logo } from '@/components/ui/Logo'
import { MessageBubble } from './MessageBubble'
import { ArrowUp, Paperclip, Image as ImageIcon } from 'lucide-react'
import { useGeneration } from '@/hooks/useGeneration'
import { useGenerationPolling } from '@/hooks/usePolling'

interface Message {
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

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState('')
  const [currentGenerationId, setCurrentGenerationId] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  
  const { mutate: generateThumbnail, isPending } = useGeneration()
  const { data: generationStatus } = useGenerationPolling(currentGenerationId || '')

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Update generation progress
  useEffect(() => {
    if (generationStatus && currentGenerationId) {
      setMessages(prev => prev.map(msg => 
        msg.id === `processing-${currentGenerationId}` 
          ? {
              ...msg,
              progress: generationStatus.progress,
              status: generationStatus.status as any,
              content: getProgressMessage(generationStatus.status, generationStatus.progress)
            }
          : msg
      ))

      // Add result message when completed
      if (generationStatus.status === 'completed' && generationStatus.result) {
        setMessages(prev => [
          ...prev.filter(msg => msg.id !== `processing-${currentGenerationId}`),
          {
            id: `result-${currentGenerationId}`,
            content: 'Thumbnail شما با موفقیت تولید شد!',
            type: 'result',
            timestamp: new Date().toISOString(),
            status: 'completed',
            result: {
              image_url: generationStatus.result.image_url,
              processing_time: generationStatus.result.processing_time
            }
          }
        ])
        setCurrentGenerationId(null)
      }
    }
  }, [generationStatus, currentGenerationId])

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
          setCurrentGenerationId(generationId)
          
          // Add processing message
          const processingMessage: Message = {
            id: `processing-${generationId}`,
            content: 'شروع تولید thumbnail...',
            type: 'system',
            timestamp: new Date().toISOString(),
            status: 'processing',
            progress: 0
          }
          
          setMessages(prev => [...prev, processingMessage])
        }
      }
    )
  }

  const getProgressMessage = (status: string, progress: number) => {
    const messages = {
      analyzing: 'در حال تحلیل درخواست شما...',
      matching_templates: 'جستجو برای بهترین template...',
      generating: 'تولید thumbnail با هوش مصنوعی...',
      processing: 'پردازش نهایی...',
      completed: 'تولید با موفقیت تکمیل شد!'
    }
    
    return messages[status as keyof typeof messages] || `در حال پردازش... ${progress}%`
  }

  const isEmpty = messages.length === 0

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Gradient Background */}
      <div className="fixed inset-0 bg-gradient-to-br from-[#E0C3FC] via-[#D5E1FF] via-[#E8F4FF] to-[#FFE5E5] -z-10" />
      
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
          className="flex items-center justify-center mb-8"
        >
          <GlassCard className="px-6 py-3">
            <div className="flex items-center gap-3">
              <Logo className="w-8 h-8" />
              <span className="font-bold text-text-primary text-lg">Routix</span>
              <span className="text-text-muted text-sm">AI Thumbnail Generator</span>
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
                  سلام! 👋
                </h1>
                <h2 className="text-2xl font-semibold text-text-primary">
                  چطور می‌تونم کمکتون کنم؟
                </h2>
                <p className="text-text-secondary text-lg">
                  برای تولید thumbnail فوق‌العاده آماده‌ام
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
                  onClick={() => setInputValue('یک thumbnail گیمینگ با انفجار و اکشن بساز')}
                />
                <QuickActionButton 
                  icon="💡" 
                  label="Tech Tutorial" 
                  onClick={() => setInputValue('thumbnail آموزشی تکنولوژی مدرن و جذاب')}
                />
                <QuickActionButton 
                  icon="🎨" 
                  label="Creative Design" 
                  onClick={() => setInputValue('thumbnail خلاقانه با طراحی منحصربفرد')}
                />
              </motion.div>
            </motion.div>
          ) : (
            // Messages List
            <div className="space-y-4">
              <AnimatePresence>
                {messages.map((message) => (
                  <MessageBubble
                    key={message.id}
                    message={message}
                    isLatest={message.id === messages[messages.length - 1]?.id}
                  />
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
                    title="اضافه کردن تصویر"
                  >
                    <ImageIcon className="w-5 h-5 text-text-muted" />
                  </button>
                  <button
                    type="button"
                    className="p-2 rounded-xl hover:bg-white/30 transition-colors"
                    title="پیوست فایل"
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
                  placeholder="درخواست thumbnail خود را بنویسید..."
                  className="flex-1 bg-transparent border-none outline-none px-4 py-3 text-text-primary placeholder:text-text-muted text-right"
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
                      <span className="font-medium mr-2">ارسال</span>
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
            برای تولید thumbnail بهتر، جزئیات بیشتری ارائه دهید
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