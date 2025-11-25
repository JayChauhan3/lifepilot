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
        // Transform frontend format to backend format
        const backendRoutine = {
            title: routine.title,
            time_of_day: routine.startTime,
            end_time: routine.endTime,
            duration: routine.duration,
            icon: routine.icon || 'FiActivity',
            is_work_block: routine.isWorkBlock || false,
            frequency: 'daily', // Default to daily
            days_of_week: [],
            is_active: true,
        };

        const response = await fetch(`${API_BASE_URL}/routines`, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify(backendRoutine),
        });

        if (!response.ok) {
            if (response.status === 401) {
                authService.removeToken();
                window.location.href = '/login';
            }
            if (response.status === 409) {
                const error = await response.json();
                throw new Error(error.detail || 'Time conflict detected');
            }
            throw new Error('Failed to create routine');
        }

        return response.json();
    },

    async updateRoutine(id: string, updates: Partial<Routine>): Promise<Routine> {
        // Transform frontend format to backend format
        const backendUpdates: any = {};

        if (updates.title !== undefined) backendUpdates.title = updates.title;
        if (updates.startTime !== undefined) backendUpdates.time_of_day = updates.startTime;
        if (updates.endTime !== undefined) backendUpdates.end_time = updates.endTime;
        if (updates.duration !== undefined) backendUpdates.duration = updates.duration;
        if (updates.icon !== undefined) backendUpdates.icon = updates.icon;
        if (updates.isWorkBlock !== undefined) backendUpdates.is_work_block = updates.isWorkBlock;

        const response = await fetch(`${API_BASE_URL}/routines/${id}`, {
            method: 'PUT',
            headers: getHeaders(),
            body: JSON.stringify(backendUpdates),
        });

        if (!response.ok) {
            if (response.status === 401) {
                authService.removeToken();
                window.location.href = '/login';
            }
            if (response.status === 409) {
                const error = await response.json();
                throw new Error(error.detail || 'Time conflict detected');
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

    async checkTimeConflicts(
        startTime: string,
        endTime: string,
        excludeId?: string
    ): Promise<Routine[]> {
        const params = new URLSearchParams({
            start_time: startTime,
            end_time: endTime,
            ...(excludeId && { exclude_id: excludeId })
        });

        const response = await fetch(
            `${API_BASE_URL}/routines/check-conflicts?${params}`,
            { headers: getHeaders() }
        );

        if (!response.ok) {
            if (response.status === 401) {
                authService.removeToken();
                window.location.href = '/login';
            }
            throw new Error('Failed to check conflicts');
        }

        return response.json();
    },
};
