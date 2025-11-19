import React from 'react'
import { useChatStore } from '@/store/chatStore'

export const ErrorDisplay: React.FC = () => {
  const { error, retryLastMessage, setError } = useChatStore()

  if (!error) return null

  return (
    <div className="mx-auto max-w-4xl px-6 md:px-20 py-3">
      <div className="bg-red-500/10 backdrop-blur-sm border border-red-500/30 rounded-xl p-4">
        <div className="flex items-start space-x-3">
          <div className="flex-shrink-0">
            <svg className="w-6 h-6 text-red-400" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="flex-1">
            <h3 className="text-sm font-medium text-red-300">Connection Error</h3>
            <p className="mt-1 text-sm text-red-400">{error}</p>
            <div className="mt-3 flex space-x-3">
              <button
                onClick={retryLastMessage}
                className="text-sm bg-red-500/20 hover:bg-red-500/30 text-red-300 px-4 py-2 rounded-lg transition-all duration-200 border border-red-500/30"
              >
                Retry
              </button>
              <button
                onClick={() => setError(null)}
                className="text-sm text-red-400 hover:text-red-300 transition-colors"
              >
                Dismiss
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
