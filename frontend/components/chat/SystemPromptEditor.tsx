import React, { ChangeEvent } from 'react'
import { useChatStore } from '@/store/chatStore'
import { Button } from '@/components/ui/Button'

export const SystemPromptEditor: React.FC = () => {
  const { systemPrompt, setSystemPrompt, toggleSystemPrompt } = useChatStore()
  
  const handleChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
    setSystemPrompt(e.target.value)
  }

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium text-white">System Prompt Editor</h3>
        <Button variant="ghost" size="sm" onClick={toggleSystemPrompt} className="text-gray-400 hover:text-white">
          Close
        </Button>
      </div>
      
      <div className="space-y-3">
        <label htmlFor="system-prompt" className="block text-sm font-medium text-gray-300">
          Configure the AI assistant's behavior and personality
        </label>
        <textarea
          id="system-prompt"
          value={systemPrompt}
          onChange={handleChange}
          rows={6}
          className="w-full px-4 py-3 text-sm bg-white/10 border border-white/20 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none text-white placeholder-gray-400 backdrop-blur-sm"
          placeholder="Enter system prompt..."
        />
      </div>
      
      <div className="flex items-center justify-between text-xs text-gray-400">
        <span>This prompt will be used for all conversations</span>
        <span>{systemPrompt.length}/500 characters</span>
      </div>
      
      <div className="bg-blue-500/10 backdrop-blur-sm border border-blue-500/30 rounded-xl p-4">
        <p className="text-sm text-blue-300">
          <strong>Tip:</strong> Be specific about the AI's role, tone, and constraints for better results.
        </p>
      </div>
    </div>
  )
}
