import { create } from 'zustand';
import { Task, Routine, TaskType } from '../types/planner';
import { plannerService } from '../services/plannerService';

interface PlannerState {
    tasks: Task[];
    routines: Routine[];
    isLoading: boolean;
    error: string | null;

    // Actions
    fetchTasks: () => Promise<void>;
    addTask: (task: Omit<Task, 'id'>) => Promise<void>;
    updateTask: (id: string, task: Partial<Task>) => Promise<void>;
    deleteTask: (id: string) => Promise<void>;
    deleteTasksByType: (type: TaskType) => Promise<void>; // For "Delete All" in a column
    toggleTaskCompletion: (id: string) => Promise<void>;

    fetchRoutines: () => Promise<void>;
    addRoutine: (routine: Omit<Routine, 'id'>) => Promise<void>;
    updateRoutine: (id: string, routine: Partial<Routine>) => Promise<void>;
    deleteRoutine: (id: string) => Promise<void>;
}

export const usePlannerStore = create<PlannerState>((set, get) => ({
    tasks: [],
    routines: [],
    isLoading: false,
    error: null,

    fetchTasks: async () => {
        set({ isLoading: true, error: null });
        try {
            const tasks = await plannerService.getTasks();
            set({ tasks, isLoading: false });
        } catch (error) {
            set({ error: 'Failed to fetch tasks', isLoading: false });
        }
    },

    addTask: async (task) => {
        set({ isLoading: true, error: null });
        try {
            const newTask = await plannerService.createTask(task);
            set((state) => ({ tasks: [...state.tasks, newTask], isLoading: false }));
        } catch (error) {
            set({ error: 'Failed to add task', isLoading: false });
        }
    },

    updateTask: async (id, updatedFields) => {
        set({ isLoading: true, error: null });
        try {
            await plannerService.updateTask(id, updatedFields);
            set((state) => ({
                tasks: state.tasks.map((t) => (t.id === id ? { ...t, ...updatedFields } : t)),
                isLoading: false,
            }));
        } catch (error) {
            set({ error: 'Failed to update task', isLoading: false });
        }
    },

    deleteTask: async (id) => {
        set({ isLoading: true, error: null });
        try {
            await plannerService.deleteTask(id);
            set((state) => ({
                tasks: state.tasks.filter((t) => t.id !== id),
                isLoading: false,
            }));
        } catch (error) {
            set({ error: 'Failed to delete task', isLoading: false });
        }
    },

    deleteTasksByType: async (type) => {
        set({ isLoading: true, error: null });
        try {
            // In a real app, we might need an API endpoint to delete by type or delete multiple
            // For now, we'll just update the local state and assume backend handles it or we loop
            const tasksToDelete = get().tasks.filter(t => t.type === type);
            await Promise.all(tasksToDelete.map(t => plannerService.deleteTask(t.id)));

            set((state) => ({
                tasks: state.tasks.filter((t) => t.type !== type),
                isLoading: false
            }));
        } catch (error) {
            set({ error: 'Failed to delete tasks', isLoading: false });
        }
    },

    toggleTaskCompletion: async (id) => {
        const task = get().tasks.find((t) => t.id === id);
        if (!task) return;

        console.log('Toggling completion for task:', id, 'Current status:', task.isCompleted);
        const newIsCompleted = !task.isCompleted;
        const newType = newIsCompleted ? 'done' : (task.date === new Date().toISOString().split('T')[0] ? 'today' : 'upcoming');

        await get().updateTask(id, { isCompleted: newIsCompleted, type: newType });
    },

    fetchRoutines: async () => {
        set({ isLoading: true, error: null });
        try {
            const routines = await plannerService.getRoutines();
            set({ routines, isLoading: false });
        } catch (error) {
            set({ error: 'Failed to fetch routines', isLoading: false });
        }
    },

    addRoutine: async (routine) => {
        set({ isLoading: true, error: null });
        try {
            const newRoutine = await plannerService.createRoutine(routine);
            await get().fetchRoutines(); // Refetch for correct order
        } catch (error: any) {
            const message = error.message || 'Failed to add routine';
            set({ error: message, isLoading: false });
            throw error; // Re-throw so modal can show error
        }
    },

    updateRoutine: async (id, updatedFields) => {
        set({ isLoading: true, error: null });
        try {
            await plannerService.updateRoutine(id, updatedFields);
            // Refetch all routines to get the correct order from backend
            await get().fetchRoutines();
        } catch (error: any) {
            const message = error.message || 'Failed to update routine';
            set({ error: message, isLoading: false });
            throw error; // Re-throw so modal can show error
        }
    },

    deleteRoutine: async (id) => {
        set({ isLoading: true, error: null });
        console.log('Deleting routine:', id);
        try {
            await plannerService.deleteRoutine(id);
            console.log('Routine deleted successfully from API');
            set((state) => ({
                routines: state.routines.filter((r) => r.id !== id),
                isLoading: false,
            }));
        } catch (error) {
            console.error('Failed to delete routine:', error);
            set({ error: 'Failed to delete routine', isLoading: false });
        }
    },
}));
