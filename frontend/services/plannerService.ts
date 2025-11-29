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

        const data = await response.json();

        // Map _id to id if needed
        return data.map((task: any) => ({
            ...task,
            id: task.id || task._id || `temp-${Math.random().toString(36).substr(2, 9)}`,
            priorityIndex: task.priorityIndex ?? task.priority_index
        }));
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

        const data = await response.json();
        return {
            ...data,
            id: data.id || data._id,
            priorityIndex: data.priorityIndex ?? data.priority_index
        };
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

        const data = await response.json();
        return {
            ...data,
            id: data.id || data._id,
            priorityIndex: data.priorityIndex ?? data.priority_index
        };
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

    async reorderTasks(taskIds: string[]): Promise<void> {
        const response = await fetch(`${API_BASE_URL}/tasks/reorder`, {
            method: 'PUT',
            headers: getHeaders(),
            body: JSON.stringify({ task_ids: taskIds }),
        });

        if (!response.ok) {
            if (response.status === 401) {
                authService.removeToken();
                window.location.href = '/login';
            }
            throw new Error('Failed to reorder tasks');
        }
    },

    async syncTasks(): Promise<{ success: boolean; warning?: boolean; message?: string }> {
        const response = await fetch(`${API_BASE_URL}/tasks/sync`, {
            method: 'POST',
            headers: getHeaders(),
        });

        if (!response.ok) {
            if (response.status === 401) {
                authService.removeToken();
                window.location.href = '/login';
            }
            throw new Error('Failed to sync tasks');
        }

        return await response.json();
    },

    // Routine operations
    async getRoutines(): Promise<Routine[]> {
        console.log('Fetching routines from:', `${API_BASE_URL}/routines`);
        const response = await fetch(`${API_BASE_URL}/routines`, {
            headers: getHeaders(),
        });

        if (!response.ok) {
            console.error('Failed to fetch routines:', response.status, response.statusText);
            if (response.status === 401) {
                authService.removeToken();
                window.location.href = '/login';
            }
            throw new Error('Failed to fetch routines');
        }

        const data = await response.json();
        console.log('Raw API response:', JSON.stringify(data, null, 2));

        // Helper function to ensure time is in 12-hour format
        const formatTimeForDisplay = (timeStr: string | undefined, defaultTime: string): string => {
            if (!timeStr) return defaultTime;

            // If already in 12h format with AM/PM, return as is
            if (timeStr.includes('AM') || timeStr.includes('PM')) {
                return timeStr;
            }

            // If in 24h format (e.g., "13:30"), convert to 12h
            if (/^\d{1,2}:\d{2}$/.test(timeStr)) {
                const [hours, minutes] = timeStr.split(':');
                const hoursNum = parseInt(hours, 10);
                const period = hoursNum >= 12 ? 'PM' : 'AM';
                const hours12 = hoursNum % 12 || 12;
                return `${hours12}:${minutes} ${period}`;
            }

            return defaultTime;
        };

        // Transform data from backend to frontend format
        const routines = data.map((routine: any) => {
            // Backend now sends startTime and endTime directly
            const startTime = routine.startTime || '6:00 AM';
            const endTime = routine.endTime || '10:00 AM';

            const routineData = {
                id: routine.id || routine._id || `temp-${Math.random().toString(36).substr(2, 9)}`,
                title: routine.title || 'Untitled Routine',
                startTime: formatTimeForDisplay(startTime, '6:00 AM'),
                endTime: formatTimeForDisplay(endTime, '10:00 AM'),
                duration: routine.duration || '4h',
                nextRun: routine.nextRun || routine.next_run || '',
                icon: routine.icon || 'FiActivity',
                isWorkBlock: routine.is_work_block || routine.isWorkBlock || false,
                isProtected: routine.is_protected || routine.isProtected || false,
                canDelete: routine.can_delete !== false && routine.canDelete !== false,
                canEditTitle: routine.can_edit_title !== false && routine.canEditTitle !== false,
                canEditTime: routine.can_edit_time !== false && routine.canEditTime !== false
            };

            console.log('Processed routine:', routineData);
            return routineData;
        });

        console.log('Final routines data:', routines);
        return routines;
    },

    async createRoutine(routine: Omit<Routine, 'id'>): Promise<Routine> {
        // Transform frontend format to backend format
        const backendRoutine = {
            title: routine.title,
            startTime: routine.startTime,
            endTime: routine.endTime,
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

            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || 'Failed to create routine');
        }

        return response.json();
    },

    async updateRoutine(id: string, updates: Partial<Routine>): Promise<Routine> {
        // Transform frontend format to backend format
        const backendUpdates: any = {};

        if (updates.title !== undefined) backendUpdates.title = updates.title;
        if (updates.startTime !== undefined) backendUpdates.startTime = updates.startTime;
        if (updates.endTime !== undefined) backendUpdates.endTime = updates.endTime;
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
            // Handle 403 for protected routines
            if (response.status === 403) {
                const error = await response.json();
                throw new Error(error.detail || 'Cannot delete this routine');
            }
            throw new Error('Failed to delete routine');
        }
    },

    async checkTimeConflicts(startTime: string, endTime: string, excludeId?: string): Promise<Routine[]> {
        try {
            // Ensure times are properly formatted
            const formatTime = (time: string): string => {
                try {
                    // Handle null/undefined/empty
                    if (!time) return '';

                    // Convert to string in case it's a number or other type
                    const timeStr = String(time).trim();

                    // If it's already in 24h format (HH:MM), return as is
                    if (/^\d{1,2}:\d{2}$/.test(timeStr)) {
                        const [hours, minutes] = timeStr.split(':').map(Number);
                        return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
                    }

                    // Handle 12h format (h:mm AM/PM)
                    if (timeStr.includes(' ')) {
                        const [timePart, period] = timeStr.split(' ');
                        if (!timePart || !period) return '';

                        const [hoursStr, minutesStr = '00'] = timePart.split(':');
                        let hours = parseInt(hoursStr, 10);
                        const minutes = parseInt(minutesStr, 10) || 0;

                        // Validate hours and minutes
                        if (isNaN(hours) || hours < 1 || hours > 12) return '';
                        if (minutes < 0 || minutes > 59) return '';

                        // Convert to 24h format
                        const periodUpper = period.toUpperCase();
                        if (periodUpper === 'PM' && hours < 12) {
                            hours += 12;
                        } else if (periodUpper === 'AM' && hours === 12) {
                            hours = 0;
                        }

                        return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
                    }

                    return ''; // Return empty string for invalid formats
                } catch (error) {
                    console.error('Error formatting time:', error, 'Input:', time);
                    return ''; // Return empty string on error
                }
            };

            const formattedStart = formatTime(startTime);
            const formattedEnd = formatTime(endTime);

            if (!formattedStart || !formattedEnd) {
                throw new Error('Invalid time format');
            }

            const params = new URLSearchParams({
                start_time: formattedStart,
                end_time: formattedEnd
            });

            if (excludeId) {
                params.append('exclude_id', excludeId);
            }

            const response = await fetch(`${API_BASE_URL}/routines/check-conflicts?${params}`, {
                headers: getHeaders(),
            });

            if (!response.ok) {
                throw new Error('Failed to check conflicts');
            }

            return await response.json();
        } catch (error) {
            console.error('Error checking conflicts:', error);
            throw error;
        }
    },
};
