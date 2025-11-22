import { apiClient } from '../lib/api';
import { Task, Routine } from '../types/planner';

export const plannerService = {
    // Tasks
    getTasks: async (): Promise<Task[]> => {
        // Mocking for now as requested, but structure ready for API
        // return apiClient.get<Task[]>('/tasks');
        return Promise.resolve([]);
    },

    createTask: async (task: Omit<Task, 'id'>): Promise<Task> => {
        // return apiClient.post<Task>('/tasks', task);
        return Promise.resolve({ ...task, id: Math.random().toString(36).substr(2, 9) });
    },

    updateTask: async (id: string, task: Partial<Task>): Promise<Task> => {
        // return apiClient.put<Task>(`/tasks/${id}`, task);
        return Promise.resolve({ ...task, id } as Task);
    },

    deleteTask: async (id: string): Promise<void> => {
        // return apiClient.delete(`/tasks/${id}`);
        return Promise.resolve();
    },

    deleteAllTasks: async (): Promise<void> => {
        // return apiClient.delete('/tasks');
        return Promise.resolve();
    },

    // Routines
    getRoutines: async (): Promise<Routine[]> => {
        // return apiClient.get<Routine[]>('/routines');
        return Promise.resolve([]);
    },

    createRoutine: async (routine: Omit<Routine, 'id'>): Promise<Routine> => {
        // return apiClient.post<Routine>('/routines', routine);
        return Promise.resolve({ ...routine, id: Math.random().toString(36).substr(2, 9) });
    },

    updateRoutine: async (id: string, routine: Partial<Routine>): Promise<Routine> => {
        // return apiClient.put<Routine>(`/routines/${id}`, routine);
        return Promise.resolve({ ...routine, id } as Routine);
    },

    deleteRoutine: async (id: string): Promise<void> => {
        // return apiClient.delete(`/routines/${id}`);
        return Promise.resolve();
    }
};
