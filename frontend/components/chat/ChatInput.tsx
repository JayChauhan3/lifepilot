import React, { useState, useRef, useEffect, KeyboardEvent, ChangeEvent } from 'react'
import { useChatStore } from '@/store/chatStore'
import { Button } from '@/components/ui/Button'

export const ChatInput: React.FC = () => {
  const { inputValue, setInputValue, sendMessageStreaming, isLoading, isStreaming, stopStreaming } = useChatStore()
  const [isFocused, setIsFocused] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const handleSend = () => {
    if (inputValue.trim() && !isLoading && !isStreaming) {
      sendMessageStreaming()
    }
  }

  const handleStop = () => {
    if (isStreaming) {
      stopStreaming()
    }
  }

  const handleKeyPress = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
    setInputValue(e.target.value)
    // Auto-resize textarea
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`
    }
  }

  // Initialize textarea height
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`
    }
  }, [])

  const isDisabled = isLoading || isStreaming

  return (
    <div className="relative">
      {/* Glow effect when focused */}
      {isFocused && (
        <div className="absolute inset-0 bg-white/10 rounded-2xl blur-xl"></div>
      )}
      
      <div className="relative bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-1 transition-all duration-300 hover:bg-white/15">
        <div className="flex flex-col gap-0">
          {/* Message Input */}
          <textarea
            ref={textareaRef}
            value={inputValue}
            onChange={handleChange}
            onKeyPress={handleKeyPress}
            placeholder={isStreaming ? "AI is responding..." : "Ask me anything..."}
            disabled={isDisabled}
            className="w-full px-4 py-3 bg-transparent border-0 rounded-xl focus:outline-none transition-colors resize-none text-base text-white placeholder-gray-400 disabled:opacity-50 disabled:cursor-not-allowed"
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            rows={1}
            style={{ maxHeight: '200px' }}
          />
          
          {/* Send Button */}
          <div className="flex justify-between items-center px-2 pb-2">
            <div className="text-xs text-gray-400">
              {isStreaming && (
                <span className="flex items-center space-x-1">
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
                  <span>AI is typing...</span>
                </span>
              )}
              {isLoading && !isStreaming && (
                <span className="flex items-center space-x-1">
                  <div className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse"></div>
                  <span>Processing...</span>
                </span>
              )}
            </div>
            
            <button
              onClick={isStreaming ? handleStop : handleSend}
              disabled={(!inputValue.trim() && !isStreaming) || (isLoading && !isStreaming)}
              className={`p-2 rounded-xl transition-all duration-200 flex items-center justify-center ${
                isStreaming 
                  ? 'bg-red-500/20 text-red-400 hover:bg-red-500/30 border border-red-500/30'
                  : inputValue.trim() && !isLoading && !isStreaming
                    ? 'bg-black text-white hover:bg-gray-800 shadow-lg hover:shadow-xl transform hover:scale-105 border border-white/20'
                    : 'bg-white/10 text-gray-400 hover:bg-white/20 disabled:opacity-50 disabled:cursor-not-allowed border border-white/20'
              }`}
            >
              {isStreaming ? (
                <>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <rect x="6" y="6" width="12" height="12" strokeWidth={2} />
                  </svg>
                </>
              ) : isLoading ? (
                <div className="w-5 h-5 border-2 border-gray-400 border-t-white rounded-full animate-spin"></div>
              ) : (
                <svg className="w-5 h-5 transform rotate-45" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
