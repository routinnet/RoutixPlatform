'use client'

import { ProtectedRoute } from '@/lib/auth'
import { ChatInterface } from '@/components/chat/ChatInterface'

export default function ChatPage() {
  return (
    <ProtectedRoute>
      <ChatInterface />
    </ProtectedRoute>
  )
}