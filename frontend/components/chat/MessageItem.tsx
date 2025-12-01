import React from 'react'
import { Message, useChatStore } from '@/store/chatStore'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

import { StructuredDataView } from '@/components/chat/StructuredDataView'

interface MessageItemProps {
  message: Message
}

export const MessageItem: React.FC<MessageItemProps> = ({ message }) => {
  const { toggleStructuredData } = useChatStore()
  const isUser = message.role === 'user'
  const isSystem = message.role === 'system'
  const isToolOutput = message.isToolOutput

  const formatTime = (date: Date) => {
    return new Intl.DateTimeFormat('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    }).format(date)
  }

  if (isSystem) {
    return (
      <div className="flex justify-center">
        <div className="bg-white/10 backdrop-blur-sm text-gray-300 px-4 py-2 rounded-full text-sm border border-white/20">
          {message.content}
        </div>
      </div>
    )
  }

  return (
    <div className={`flex items-start ${isUser ? 'justify-end' : ''}`}>
      <div className={`group relative max-w-2xl ${isUser ? 'ml-auto' : ''}`}>
        <div className={`flex items-center space-x-2 mb-2 ${isUser ? 'justify-end' : ''}`}>
          <span className="text-xs text-gray-400">
            {formatTime(message.timestamp)}
          </span>
          {message.agentUsed && (
            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-500/20 text-green-300 border border-green-500/30">
              🤖 {message.agentUsed}
            </span>
          )}
          {isToolOutput && (
            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-500/20 text-blue-300 border border-blue-500/30">
              {message.toolName}
            </span>
          )}
          {message.processingTime && (
            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-500/20 text-gray-300 border border-gray-500/30">
              ⏱️ {(message.processingTime * 1000).toFixed(0)}ms
            </span>
          )}
        </div>

        <div className={`relative rounded-2xl p-4 backdrop-blur-sm border transition-all duration-200 hover:shadow-xl ${isUser
          ? 'bg-[#303030] border-white/20 ml-auto'
          : 'bg-white/10 border-white/20'
          }`}>
          <div className={`text-sm leading-relaxed ${isUser ? 'text-white' : 'text-gray-200'}`}>
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                table: ({ node, ...props }) => (
                  <div className="overflow-x-auto my-4 rounded-lg border border-gray-600">
                    <table className="w-full border-collapse bg-gray-800/50" {...props} />
                  </div>
                ),
                thead: ({ node, ...props }) => <thead className="bg-gray-700/50" {...props} />,
                th: ({ node, ...props }) => <th className="px-4 py-2 text-left font-semibold text-gray-200 border-b border-gray-600" {...props} />,
                td: ({ node, ...props }) => <td className="px-4 py-2 text-gray-300 border-b border-gray-700" {...props} />,
                h1: ({ node, ...props }) => <h1 className="text-2xl font-bold mt-6 mb-4 text-white flex items-center gap-2" {...props} />,
                h2: ({ node, ...props }) => <h2 className="text-xl font-semibold mt-6 mb-4 text-white flex items-center gap-2" {...props} />,
                h3: ({ node, ...props }) => <h3 className="text-lg font-semibold mt-6 mb-3 text-white flex items-center gap-2" {...props} />,
                ul: ({ node, ...props }) => <ul className="mb-4 space-y-1 list-disc list-outside pl-5" {...props} />,
                ol: ({ node, ...props }) => <ol className="mb-4 space-y-1 list-decimal list-outside pl-5" {...props} />,
                li: ({ node, ...props }) => <li className="text-gray-300 pl-1" {...props} />,
                code: ({ node, inline, className, children, ...props }: any) => {
                  return inline ? (
                    <code className="bg-gray-800 rounded px-2 py-1 text-sm border border-gray-700 text-gray-300" {...props}>
                      {children}
                    </code>
                  ) : (
                    <pre className="bg-gray-900 rounded-lg p-4 text-sm overflow-x-auto my-4 border border-gray-700">
                      <code className="text-gray-300" {...props}>
                        {children}
                      </code>
                    </pre>
                  )
                },
                p: ({ node, ...props }) => <p className="mb-4 last:mb-0" {...props} />,
                a: ({ node, ...props }) => <a className="text-blue-400 hover:underline" target="_blank" rel="noopener noreferrer" {...props} />,
                hr: ({ node, ...props }) => <hr className="my-6 border-gray-600" {...props} />,
                blockquote: ({ node, ...props }) => <blockquote className="border-l-4 border-gray-500 pl-4 italic my-4 text-gray-400" {...props} />,
              }}
            >
              {message.content}
            </ReactMarkdown>
          </div>

          {message.toolsUsed && message.toolsUsed.length > 0 && (
            <div className="mt-3 pt-3 border-t border-white/10">
              <div className="flex items-center space-x-2">
                <span className="text-xs text-gray-400">Tools used:</span>
                <div className="flex flex-wrap gap-1">
                  {message.toolsUsed.map((tool, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-purple-500/20 text-purple-300 border border-purple-500/30"
                    >
                      🔧 {tool}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
