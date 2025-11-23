import { Task, Routine } from '../types/planner';
import { authService } from './authService';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

// Helper to get headers with auth token
const getHeaders = (): HeadersInit => {
    return {
        'Content-Type': 'application/json',
        ...authService.getAuthHeaders(),
    };
};

export const plannerService = {
    // Task operations
    async getTasks(): Promise<Task[]> {
        const response = await fetch(`${API_BASE_URL}/tasks`, {
            headers: getHeaders(),
        });

        if (!response.ok) {
            if (response.status === 401) {
                authService.removeToken();
                window.location.href = '/login';
            }
            throw new Error('Failed to fetch tasks');
        }

        return response.json();
    },

    async createTask(task: Omit<Task, 'id'>): Promise<Task> {
        const response = await fetch(`${API_BASE_URL}/tasks`, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify(task),
        });

        if (!response.ok) {
            if (response.status === 401) {
                authService.removeToken();
                window.location.href = '/login';
            }
            throw new Error('Failed to create task');
        }

        return response.json();
    },

    async updateTask(id: string, updates: Partial<Task>): Promise<Task> {
        const response = await fetch(`${API_BASE_URL}/tasks/${id}`, {
            method: 'PUT',
            headers: getHeaders(),
            body: JSON.stringify(updates),
        });

        if (!response.ok) {
            if (response.status === 401) {
                authService.removeToken();
                window.location.href = '/login';
            }
            throw new Error('Failed to update task');
        }

        return response.json();
    },

    async deleteTask(id: string): Promise<void> {
        const response = await fetch(`${API_BASE_URL}/tasks/${id}`, {
            method: 'DELETE',
            headers: getHeaders(),
        });

        if (!response.ok) {
            if (response.status === 401) {
                authService.removeToken();
                window.location.href = '/login';
            }
            throw new Error('Failed to delete task');
        }
    },

    async deleteAllTasks(): Promise<void> {
        // TODO: Implement bulk delete endpoint
        return Promise.resolve();
    },

    // Routine operations
    async getRoutines(): Promise<Routine[]> {
        const response = await fetch(`${API_BASE_URL}/routines`, {
            headers: getHeaders(),
        });

        if (!response.ok) {
            if (response.status === 401) {
                authService.removeToken();
                window.location.href = '/login';
            }
            throw new Error('Failed to fetch routines');
        }

        return response.json();
    },

    async createRoutine(routine: Omit<Routine, 'id'>): Promise<Routine> {
        const response = await fetch(`${API_BASE_URL}/routines`, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify(routine),
        });

        if (!response.ok) {
            if (response.status === 401) {
                authService.removeToken();
                window.location.href = '/login';
            }
            throw new Error('Failed to create routine');
        }

        return response.json();
    },

    async updateRoutine(id: string, updates: Partial<Routine>): Promise<Routine> {
        const response = await fetch(`${API_BASE_URL}/routines/${id}`, {
            method: 'PUT',
            headers: getHeaders(),
            body: JSON.stringify(updates),
        });

        if (!response.ok) {
            if (response.status === 401) {
                authService.removeToken();
                window.location.href = '/login';
            }
            throw new Error('Failed to update routine');
        }

        return response.json();
    },

    async deleteRoutine(id: string): Promise<void> {
        const response = await fetch(`${API_BASE_URL}/routines/${id}`, {
            method: 'DELETE',
            headers: getHeaders(),
        });

        if (!response.ok) {
            if (response.status === 401) {
                authService.removeToken();
                window.location.href = '/login';
            }
            throw new Error('Failed to delete routine');
        }
    },
};
