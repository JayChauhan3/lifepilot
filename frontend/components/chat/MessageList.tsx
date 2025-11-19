import React, { useEffect, useRef } from 'react'
import { useChatStore } from '@/store/chatStore'
import { MessageItem } from '@/components/chat/MessageItem'
import { TypingIndicator } from '@/components/chat/TypingIndicator'
import { ErrorDisplay } from '@/components/chat/ErrorDisplay'
import { StreamingIndicator } from '@/components/chat/StreamingIndicator'

export const MessageList: React.FC = () => {
  const { messages, isTyping, isStreaming } = useChatStore()
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const isInitialLoad = useRef(true)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    // Only scroll when new messages are added, not on initial load
    if (!isInitialLoad.current && messages.length > 0) {
      scrollToBottom()
    }
    // Mark initial load as complete after first render
    isInitialLoad.current = false
  }, [messages, isTyping, isStreaming])

  return (
    <div className="min-h-full pt-16 pb-32 bg-black">
      <div className="max-w-4xl mx-auto px-6 md:px-20 py-8 space-y-6">
        {messages.length === 0 && (
          <div className="text-center py-20">
            <div className="w-20 h-20 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-6 shadow-lg">
              <span className="text-white text-3xl font-bold">LP</span>
            </div>
            <h2 className="text-2xl font-bold text-white mb-2">Welcome to LifePilot</h2>
            <p className="text-gray-400 max-w-md mx-auto">
              Your personal AI assistant is ready to help. Ask me anything!
            </p>
          </div>
        )}
        
        {messages.map((message) => (
          <MessageItem key={message.id} message={message} />
        ))}
        
        <ErrorDisplay />
        
        {isTyping && <TypingIndicator />}
        
        {isStreaming && <StreamingIndicator />}
        
        <div ref={messagesEndRef} />
      </div>
    </div>
  )
}
