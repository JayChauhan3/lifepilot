// API types and client
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ChatRequest {
  user_id: string;
  message: string;
}

export interface ChatResponse {
  response: string;
  agent_used?: string;
  tools_used?: string[];
  processing_time?: number;
  message_type?: string;
  data?: Record<string, any>;
}

export interface WorkflowRequest {
  user_id: string;
  request: string;
  context?: Record<string, any>;
}

export interface WorkflowStatus {
  workflow_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'paused';
  current_step?: string;
  steps: Array<{
    step_id: string;
    action: string;
    status: string;
    agent: string;
  }>;
  created_at: string;
  started_at?: string;
  completed_at?: string;
}

export class ApiClient {
  private baseURL: string
  private userId: string | null = null

  constructor() {
    this.baseURL = API_BASE_URL
    this.userId = this.getUserId();
  }

  private getUserId(): string {
    // Check if we're in browser environment
    if (typeof window === 'undefined') {
      // Return a temporary ID for server-side rendering
      return 'temp_ssr_user_id';
    }

    // Try to get from localStorage first
    let userId = localStorage.getItem('lifepilot_user_id');
    if (!userId) {
      // Generate new user ID if not exists
      userId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem('lifepilot_user_id', userId);
    }
    return userId;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    console.log('Making request to:', url);

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    };

    // Add user ID header
    if (this.userId) {
      headers['X-User-ID'] = this.userId;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
        credentials: 'include', // Ensure cookies are sent
      });

      console.log('🌐 [API] Response received:', {
        url,
        status: response.status,
        statusText: response.statusText,
        hasCookies: document.cookie.includes('session_id'),
        cookies: document.cookie
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('API error response:', errorText);
        throw new Error(`API error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      console.log('Response data:', data);
      return data;
    } catch (error) {
      console.error('Request failed:', error);
      throw error;
    }
  }

  async chat(message: string): Promise<ChatResponse> {
    console.log('Making chat request to:', `${this.baseURL}/api/chat`);
    console.log('Request payload:', { user_id: this.userId, message });

    const response = await this.request<ChatResponse>('/api/chat', {
      method: 'POST',
      body: JSON.stringify({
        user_id: this.userId,
        message,
      } as ChatRequest),
    });

    console.log('Chat response:', response);
    return response;
  }

  async createWorkflow(request: string, context?: Record<string, any>): Promise<{ workflow_id: string }> {
    const response = await this.request<{ workflow_id: string }>('/api/workflows', {
      method: 'POST',
      body: JSON.stringify({
        user_id: this.userId,
        request,
        context,
      } as WorkflowRequest),
    });

    return response;
  }

  async getWorkflowStatus(workflowId: string): Promise<WorkflowStatus> {
    const response = await this.request<WorkflowStatus>(`/api/workflows/${workflowId}`);
    return response;
  }

  async pauseWorkflow(workflowId: string): Promise<{ success: boolean }> {
    const response = await this.request<{ success: boolean }>(`/api/workflows/${workflowId}/pause`, {
      method: 'POST',
    });
    return response;
  }

  async resumeWorkflow(workflowId: string): Promise<{ success: boolean }> {
    const response = await this.request<{ success: boolean }>(`/api/workflows/${workflowId}/resume`, {
      method: 'POST',
    });
    return response;
  }

  async cancelWorkflow(workflowId: string): Promise<{ success: boolean }> {
    const response = await this.request<{ success: boolean }>(`/api/workflows/${workflowId}/cancel`, {
      method: 'POST',
    });
    return response;
  }

  async *chatStream(message: string): AsyncGenerator<{ type: string; data: string | unknown }, void, unknown> {
    const url = `${this.baseURL}/api/chat/stream`;

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    // Add user ID header
    if (this.userId) {
      headers['X-User-ID'] = this.userId;
    }

    const response = await fetch(url, {
      method: 'POST',
      headers,
      credentials: 'include', // Ensure cookies are sent
      body: JSON.stringify({
        user_id: this.userId,
        message,
      } as ChatRequest),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) {
      throw new Error('Response body is not readable');
    }

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = line.slice(6);
              if (data === '[DONE]') {
                return;
              }
              const parsed = JSON.parse(data);
              yield parsed;
            } catch (e) {
              // Skip invalid JSON
              continue;
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  }

  async getChatHistory(): Promise<{ messages: any[] }> {
    console.log('🌐 [API] getChatHistory called')
    console.log('🌐 [API] Request URL:', `${this.baseURL}/api/chat/history`)
    console.log('🌐 [API] Credentials:', 'include')

    const response = await this.request<{ messages: any[] }>('/api/chat/history');

    console.log('🌐 [API] getChatHistory response:', {
      messageCount: response.messages?.length || 0,
      hasMessages: !!response.messages
    })

    return response;
  }
}

// Create singleton instance
export const apiClient = new ApiClient();
