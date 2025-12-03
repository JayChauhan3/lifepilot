import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import { apiClient } from '@/lib/api'

export interface Message {
  id: string
  content: string
  role: 'user' | 'assistant' | 'system'
  timestamp: Date
  structuredData?: any
  isToolOutput?: boolean
  toolName?: string
  showStructuredData?: boolean
  agentUsed?: string
  toolsUsed?: string[]
  processingTime?: number
  messageType?: string
}

interface ToolOutput {
  name: string
  data: any
  type: 'file' | 'link' | 'data'
}

interface ChatStore {
  // State
  messages: Message[]
  isLoading: boolean
  isTyping: boolean
  inputValue: string
  systemPrompt: string
  isSystemPromptExpanded: boolean
  streamingContent: string
  isStreaming: boolean
  error: string | null

  // Actions
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void
  setLoading: (loading: boolean) => void
  setTyping: (typing: boolean) => void
  setInputValue: (value: string) => void
  setSystemPrompt: (prompt: string) => void
  toggleSystemPrompt: () => void
  clearMessages: () => void
  sendMessage: () => Promise<void>
  sendMessageStreaming: () => Promise<void>
  startStreaming: () => void
  updateStreamingContent: (content: string) => void
  stopStreaming: () => void
  toggleStructuredData: (messageId: string) => void
  setError: (error: string | null) => void
  retryLastMessage: () => Promise<void>
  loadChatHistory: () => Promise<void>
}

export const useChatStore = create<ChatStore>()(
  devtools(
    (set, get) => ({
      // Initial state - empty messages, will load from localStorage
      messages: [],
      isLoading: false,
      isTyping: false,
      inputValue: '',
      systemPrompt: 'You are a helpful AI assistant for LifePilot. Provide clear, concise, and actionable responses.',
      isSystemPromptExpanded: false,
      streamingContent: '',
      isStreaming: false,
      error: null,

      // Actions
      addMessage: (message) => {
        const newMessage: Message = {
          ...message,
          id: crypto.randomUUID(),
          timestamp: new Date(),
        }

        set((state) => ({
          messages: [...state.messages, newMessage],
        }))
      },

      setLoading: (loading) => set({ isLoading: loading }),

      setTyping: (typing) => set({ isTyping: typing }),

      setInputValue: (value) => set({ inputValue: value }),

      setSystemPrompt: (prompt) => set({ systemPrompt: prompt }),

      toggleSystemPrompt: () => set((state) => ({
        isSystemPromptExpanded: !state.isSystemPromptExpanded
      })),

      clearMessages: () => set({ messages: [] }),

      sendMessage: async () => {
        const { inputValue, addMessage, setLoading, setInputValue, setError } = get()
        if (!inputValue.trim()) return

        // Add user message
        addMessage({
          content: inputValue,
          role: 'user',
        })

        setInputValue('')
        setLoading(true)
        setError(null)

        try {
          const response = await apiClient.chat(inputValue)
          addMessage({
            content: response.response,
            role: 'assistant',
            agentUsed: response.agent_used,
            toolsUsed: response.tools_used,
            processingTime: response.processing_time,
            messageType: response.message_type,
            structuredData: response.data,
            showStructuredData: !!response.data,
          })
        } catch (error) {
          console.error('Chat error:', error)
          setError(error instanceof Error ? error.message : 'Failed to send message')
          addMessage({
            content: 'Sorry, I encountered an error while processing your message. Please try again.',
            role: 'assistant',
          })
        } finally {
          setLoading(false)
        }
      },

      sendMessageStreaming: async () => {
        const { inputValue, addMessage, startStreaming, stopStreaming, setInputValue, setError, updateStreamingContent } = get()
        if (!inputValue.trim()) return

        // Add user message
        addMessage({
          content: inputValue,
          role: 'user',
        })

        setInputValue('')
        setError(null)
        startStreaming()

        // Add empty assistant message for streaming
        const assistantMessageId = crypto.randomUUID()
        set((state) => ({
          messages: [...state.messages, {
            id: assistantMessageId,
            content: '',
            role: 'assistant',
            timestamp: new Date(),
          }]
        }))

        try {
          let accumulatedContent = ''
          for await (const chunk of apiClient.chatStream(inputValue)) {
            accumulatedContent += chunk
            updateStreamingContent(accumulatedContent)

            // Update the message in real-time
            set((state) => ({
              messages: state.messages.map(msg =>
                msg.id === assistantMessageId
                  ? { ...msg, content: accumulatedContent }
                  : msg
              )
            }))
          }
        } catch (error) {
          console.error('Streaming error:', error)
          setError(error instanceof Error ? error.message : 'Failed to stream response')

          // Update with error message
          set((state) => ({
            messages: state.messages.map(msg =>
              msg.id === assistantMessageId
                ? { ...msg, content: 'Sorry, I encountered an error while processing your message. Please try again.' }
                : msg
            )
          }))
        } finally {
          stopStreaming()
        }
      },

      startStreaming: () => set({ isStreaming: true, streamingContent: '' }),

      updateStreamingContent: (content) => set({ streamingContent: content }),

      stopStreaming: () => set({ isStreaming: false, streamingContent: '' }),

      setError: (error) => set({ error }),

      retryLastMessage: async () => {
        const { messages, sendMessage, setInputValue } = get()
        const lastUserMessage = messages.filter(m => m.role === 'user').pop()
        if (lastUserMessage) {
          setInputValue(lastUserMessage.content)
          await sendMessage()
        }
      },

      toggleStructuredData: (messageId) => set((state) => ({
        messages: state.messages.map(msg =>
          msg.id === messageId
            ? { ...msg, showStructuredData: !msg.showStructuredData }
            : msg
        )
      })),

      loadChatHistory: async () => {
        try {
          const { messages } = await apiClient.getChatHistory()
          if (messages && messages.length > 0) {
            set({
              messages: messages.map(msg => ({
                ...msg,
                id: crypto.randomUUID(), // Generate ID if missing
                timestamp: new Date(msg.timestamp)
              }))
            })
          }
        } catch (error) {
          console.error('Failed to load chat history:', error)
        }
      },
    }),
    {
      name: 'Chat Store',
    }
  )
)
