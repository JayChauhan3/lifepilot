import React from 'react'
import { useChatStore } from '@/store/chatStore'
import { Button } from '@/components/ui/Button'

export const ChatHeader: React.FC = () => {
  const { toggleSystemPrompt, isSystemPromptExpanded, clearMessages } = useChatStore()

  return (
    <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-white">
      <div className="flex items-center space-x-3">
        <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
          <span className="text-white text-sm font-semibold">LP</span>
        </div>
        <div>
          <h1 className="text-lg font-semibold text-gray-900">LifePilot Assistant</h1>
          <p className="text-sm text-gray-500">Always here to help</p>
        </div>
      </div>
      
      <div className="flex items-center space-x-2">
        <Button
          variant="secondary"
          size="sm"
          onClick={toggleSystemPrompt}
          className={isSystemPromptExpanded ? 'bg-blue-50 border-blue-200' : ''}
        >
          {isSystemPromptExpanded ? 'Hide' : 'Show'} System
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={clearMessages}
          className="text-red-600 hover:text-red-700 hover:bg-red-50"
        >
          Clear
        </Button>
      </div>
    </div>
  )
}
