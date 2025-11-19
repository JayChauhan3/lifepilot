import React from 'react'
import { useChatStore } from '@/store/chatStore'

export const StreamingIndicator: React.FC = () => {
  const { isStreaming, streamingContent } = useChatStore()

  if (!isStreaming) return null

  return (
    <div className="mx-auto max-w-4xl px-6 md:px-20 py-3">
      <div className="flex items-start space-x-3">
        <div className="w-10 h-10 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-full flex items-center justify-center flex-shrink-0 shadow-lg">
          <span className="text-white text-sm font-bold">LP</span>
        </div>
        <div className="flex-1">
          <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl p-4 max-w-3xl shadow-xl">
            <div className="flex items-center space-x-2 mb-2">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
              <span className="text-xs text-gray-400">AI is thinking...</span>
            </div>
            {streamingContent && (
              <div className="text-sm text-gray-200 whitespace-pre-wrap">
                {streamingContent}
                <span className="inline-block w-2 h-4 bg-blue-400 animate-pulse ml-1"></span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
