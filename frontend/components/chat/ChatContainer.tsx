import React from 'react'
import { MessageList } from '@/components/chat/MessageList'
import { ChatInput } from '@/components/chat/ChatInput'
import { SystemPromptEditor } from '@/components/chat/SystemPromptEditor'
import { useChatStore } from '@/store/chatStore'

export const ChatContainer: React.FC = () => {
  const { isSystemPromptExpanded, clearMessages, toggleSystemPrompt } = useChatStore()

  return (
    <div className="relative h-screen bg-gradient-to-br from-gray-900 via-black to-gray-900">
      {/* Animated background gradient */}
      <div className="absolute inset-0 bg-gradient-to-r from-blue-600/10 via-purple-600/10 to-pink-600/10 animate-pulse"></div>

      {/* Messages Area - Full height scrollable */}
      <div className="absolute inset-0 overflow-y-auto">
        <MessageList />
      </div>

      {/* Input Area - Fixed at bottom with glassmorphism */}
      <div className="absolute bottom-0 left-0 right-0 z-10">
        <div className="max-w-4xl mx-auto px-6 md:px-20 py-6">
          <ChatInput />
        </div>
      </div>

      {/* System Prompt Editor - Enhanced popup */}
      {isSystemPromptExpanded && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-6">
          <div className="bg-gray-900 rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden border border-white/20">
            <div className="flex items-center justify-between p-6 border-b border-white/10 bg-gray-800/50">
              <div>
                <h3 className="text-xl font-semibold text-white">System Prompt</h3>
                <p className="text-gray-400 text-sm mt-1">Customize the AI's behavior and personality</p>
              </div>
              <button
                onClick={toggleSystemPrompt}
                className="p-2 text-gray-400 hover:text-white hover:bg-white/10 rounded-lg transition-all duration-200"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="p-6 overflow-y-auto max-h-[70vh]">
              <SystemPromptEditor />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
