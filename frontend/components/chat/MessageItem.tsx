import React from 'react'
import { Message, useChatStore } from '@/store/chatStore'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'

interface MessageItemProps {
  message: Message
}

export const MessageItem: React.FC<MessageItemProps> = ({ message }) => {
  const { toggleStructuredData } = useChatStore()
  const isUser = message.role === 'user'
  const isSystem = message.role === 'system'
  const isToolOutput = message.isToolOutput

  const formatMessageContent = (content: string) => {
    // Convert markdown-style formatting to HTML
    let formatted = content
    
    // Clean up excessive line breaks first
    formatted = formatted.replace(/\n{3,}/g, '\n\n')
    
    // Handle tables - convert markdown tables to HTML tables
    formatted = formatted.replace(/\|(.+)\|[\r\n]+\|[-\s\|]+\|[\r\n]+((?:\|.+\|[\r\n]*)+)/g, (match: string, header: string, body: string) => {
      const headerCells = header.split('|').map((cell: string) => cell.trim()).filter((cell: string) => cell)
      const bodyRows = body.trim().split('\n').map((row: string) => 
        row.split('|').map((cell: string) => cell.trim()).filter((cell: string) => cell)
      )
      
      const headerHtml = headerCells.map((cell: string) => `<th class="px-4 py-2 text-left font-semibold text-gray-200 border-b border-gray-600">${cell}</th>`).join('')
      const bodyHtml = bodyRows.map((row: string[]) => {
        const cellsHtml = row.map((cell: string) => `<td class="px-4 py-2 text-gray-300 border-b border-gray-700">${cell}</td>`).join('')
        return `<tr>${cellsHtml}</tr>`
      }).join('')
      
      return `<table class="w-full border-collapse border border-gray-600 rounded-lg overflow-hidden my-4"><thead><tr>${headerHtml}</tr></thead><tbody>${bodyHtml}</tbody></table>`
    })
    
    // Headers with emojis - make them more prominent
    formatted = formatted.replace(/^### (.*$)/gim, '<h3 class="text-lg font-semibold mt-6 mb-3 text-white flex items-center gap-2">$1</h3>')
    formatted = formatted.replace(/^## (.*$)/gim, '<h2 class="text-xl font-semibold mt-6 mb-4 text-white flex items-center gap-2">$1</h2>')
    formatted = formatted.replace(/^# (.*$)/gim, '<h1 class="text-2xl font-bold mt-6 mb-4 text-white flex items-center gap-2">$1</h1>')
    
    // Bold text
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-white">$1</strong>')
    
    // Italic text
    formatted = formatted.replace(/\*(.*?)\*/g, '<em class="italic text-gray-300">$1</em>')
    
    // Clean up duplicate bullet points that might appear
    formatted = formatted.replace(/^([*•-])\s+(.*)$/gim, (match: string, bullet: string, content: string) => {
      // Remove any leading bullet characters from content
      const cleanContent = content.replace(/^([*•-])\s+/, '')
      return `<li className="ml-4 mb-2">• ${cleanContent}</li>`
    })
    
    // Numbered lists with proper spacing
    formatted = formatted.replace(/^(\d+\.\s)(.*)$/gim, (match: string, number: string, content: string) => {
      return `<li className="ml-4 mb-2 list-decimal">${number}${content}</li>`
    })
    
    // Handle horizontal rules
    formatted = formatted.replace(/^---$/gim, '<hr class="my-6 border-gray-600" />')
    
    // Code blocks with syntax highlighting appearance
    formatted = formatted.replace(/```(\w+)?[\s\S]*?```/g, '<pre class="bg-gray-900 rounded-lg p-4 text-sm overflow-x-auto my-4 border border-gray-700"><code class="text-gray-300">$&</code></pre>')
    
    // Inline code
    formatted = formatted.replace(/`(.*?)`/g, '<code class="bg-gray-800 rounded px-2 py-1 text-sm border border-gray-700 text-gray-300">$1</code>')
    
    // Convert line breaks to paragraphs with proper spacing
    const paragraphs = formatted.split('\n\n').filter(p => p.trim())
    formatted = paragraphs.map(paragraph => {
      // If it's a list item, don't wrap in paragraph
      if (paragraph.includes('<li')) {
        return `<ul class="mb-4 space-y-1">${paragraph}</ul>`
      }
      // If it's already a header, table, or code block, don't wrap in paragraph
      if (paragraph.includes('<h') || paragraph.includes('<table') || paragraph.includes('<pre') || paragraph.includes('<hr')) {
        return paragraph
      }
      // Regular paragraph
      return `<p class="mb-4 text-gray-300 leading-relaxed">${paragraph}</p>`
    }).join('')
    
    // Clean up any remaining multiple line breaks
    formatted = formatted.replace(/\n{2,}/g, '\n')
    
    return formatted
  }

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
        
        <div className={`relative rounded-2xl p-4 backdrop-blur-sm border transition-all duration-200 hover:shadow-xl ${
          isUser 
            ? 'bg-[#303030] border-white/20 ml-auto'
            : 'bg-white/10 border-white/20'
        }`}>
          <div 
            className={`text-sm leading-relaxed ${isUser ? 'text-white' : 'text-gray-200'}`}
            dangerouslySetInnerHTML={{ __html: formatMessageContent(message.content) }}
          />
          
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
          
          {isToolOutput && message.structuredData && (
            <div className="mt-4 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-gray-400">Structured Data</span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => toggleStructuredData(message.id)}
                  className="text-xs text-gray-400 hover:text-white"
                >
                  {message.showStructuredData ? 'Hide' : 'Show'} JSON
                </Button>
              </div>
              
              {message.showStructuredData ? (
                <div className="bg-gray-800/50 rounded-xl p-3 border border-gray-700">
                  <pre className="text-xs text-gray-300 overflow-x-auto whitespace-pre-wrap">
                    {JSON.stringify(message.structuredData, null, 2)}
                  </pre>
                </div>
              ) : (
                <StructuredDataDisplay data={message.structuredData} />
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

interface StructuredDataDisplayProps {
  data: any
}

const StructuredDataDisplay: React.FC<StructuredDataDisplayProps> = ({ data }) => {
  if (data.items && Array.isArray(data.items)) {
    return (
      <div className="space-y-3">
        {data.items.map((category: any, index: number) => (
          <div key={index} className="bg-white/5 rounded-xl p-3 border border-white/10">
            <h4 className="font-medium text-white mb-2">{category.category}</h4>
            <div className="flex flex-wrap gap-2">
              {category.items.map((item: string, itemIndex: number) => (
                <span
                  key={itemIndex}
                  className="inline-flex items-center px-3 py-1 rounded-lg text-sm bg-white/10 border border-white/20 text-gray-300"
                >
                  {item}
                </span>
              ))}
            </div>
          </div>
        ))}
        {data.totalItems && (
          <div className="text-sm text-gray-400 border-t border-white/10 pt-2">
            Total items: {data.totalItems}
          </div>
        )}
        {data.estimatedCost && (
          <div className="text-sm text-gray-400">
            Estimated cost: {data.estimatedCost}
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="bg-white/5 rounded-xl p-3 border border-white/10">
      <pre className="text-sm text-gray-300 whitespace-pre-wrap">
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  )
}
