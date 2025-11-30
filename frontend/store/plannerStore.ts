import { create } from 'zustand';
import { Task, Routine, TaskType } from '../types/planner';
import { plannerService } from '../services/plannerService';

interface PlannerState {
    tasks: Task[];
    historyTasks: Task[];
    routines: Routine[];
    isLoading: boolean;
    error: string | null;
    workBlockWarning: string | null;

    // Actions
    fetchTasks: () => Promise<void>;
    fetchTaskHistory: () => Promise<void>;
    addTask: (task: Omit<Task, 'id'>) => Promise<void>;
    updateTask: (id: string, updates: Partial<Task>) => Promise<void>;
    deleteTask: (id: string) => Promise<void>;
    deleteTasksByType: (type: TaskType) => Promise<void>; // For "Delete All" in a column
    toggleTaskCompletion: (id: string) => Promise<void>;
    reorderTasks: (taskIds: string[]) => Promise<void>;
    syncTasks: () => Promise<void>;

    fetchRoutines: () => Promise<void>;
    addRoutine: (routine: Omit<Routine, 'id'>) => Promise<void>;
    updateRoutine: (id: string, updates: Partial<Routine>) => Promise<void>;
    deleteRoutine: (id: string) => Promise<void>;
    toggleRoutineCompletion: (id: string, date: string) => Promise<void>;
}

export const usePlannerStore = create<PlannerState>((set, get) => ({
    tasks: [],
    historyTasks: [],
    routines: [],
    isLoading: false,
    error: null,
    workBlockWarning: null,

    fetchTasks: async () => {
        set({ isLoading: true, error: null });
        try {
            const tasks = await plannerService.getTasks();
            set({ tasks, isLoading: false });
        } catch (error) {
            set({ error: (error as Error).message, isLoading: false });
        }
    },

    fetchTaskHistory: async () => {
        set({ isLoading: true, error: null });
        try {
            const historyTasks = await plannerService.getTaskHistory();
            set({ historyTasks, isLoading: false });
        } catch (error) {
            set({ error: (error as Error).message, isLoading: false });
        }
    },

    addTask: async (task) => {
        set({ isLoading: true, error: null });
        try {
            const newTask = await plannerService.createTask(task);
            set((state) => ({ tasks: [...state.tasks, newTask], isLoading: false }));
            // Check work block capacity after adding
            get().syncTasks();
        } catch (error) {
            set({ error: (error as Error).message, isLoading: false });
        }
    },

    updateTask: async (id, updates) => {
        set({ isLoading: true, error: null });
        try {
            const updatedTask = await plannerService.updateTask(id, updates);
            set((state) => ({
                tasks: state.tasks.map((t) => (t.id === id ? updatedTask : t)),
                isLoading: false,
            }));
            // Check work block capacity after update
            get().syncTasks();
        } catch (error) {
            set({ error: (error as Error).message, isLoading: false });
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
            set({ error: (error as Error).message, isLoading: false });
        }
    },

    deleteTasksByType: async (type) => {
        set({ isLoading: true, error: null });
        try {
            await plannerService.deleteTasksByType(type);
            set((state) => ({
                tasks: state.tasks.filter((t) => t.type !== type),
                isLoading: false
            }));
        } catch (error) {
            set({ error: (error as Error).message, isLoading: false });
        }
    },

    toggleTaskCompletion: async (id) => {
        set({ error: null });
        try {
            const updatedTask = await plannerService.toggleTaskCompletion(id);
            set((state) => ({
                tasks: state.tasks.map((t) => (t.id === id ? updatedTask : t)),
            }));
        } catch (error) {
            set({ error: (error as Error).message });
        }
    },

    reorderTasks: async (taskIds) => {
        console.log('Store: reorderTasks called with', taskIds);
        // Optimistic update: Reorder tasks in state based on taskIds
        set((state) => {
            const taskMap = new Map(state.tasks.map(t => [t.id, t]));
            const reorderedTasks = taskIds
                .map(id => taskMap.get(id))
                .filter((t): t is Task => t !== undefined);

            // Keep tasks that are NOT in the reordered list (e.g. other columns)
            const otherTasks = state.tasks.filter(t => !taskIds.includes(t.id));

            const newTasks = [...reorderedTasks, ...otherTasks];
            console.log('Store: Optimistic update complete. New tasks count:', newTasks.length);
            return { tasks: newTasks };
        });

        try {
            await plannerService.reorderTasks(taskIds);
            console.log('Store: Backend reorder success');
        } catch (error) {
            console.error('Store: Backend reorder failed', error);
            set({ error: (error as Error).message });
            // TODO: Revert state if needed, but fetchTasks usually refreshes it
            get().fetchTasks();
        }
    },

    syncTasks: async () => {
        try {
            const result = await plannerService.syncTasks();

            // Set warning if capacity exceeded
            if (result.warning) {
                set({ workBlockWarning: result.message || null });
            } else {
                set({ workBlockWarning: null });
            }

            // Refresh tasks after sync
            await get().fetchTasks();
        } catch (error) {
            console.error('Failed to sync tasks', error);
            set({ error: 'Failed to sync tasks' });
        }
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

    toggleRoutineCompletion: async (id, date) => {
        set({ error: null });
        try {
            const updatedRoutine = await plannerService.toggleRoutineCompletion(id, date);
            set((state) => ({
                routines: state.routines.map((r) => (r.id === id ? updatedRoutine : r)),
            }));
        } catch (error) {
            set({ error: (error as Error).message });
        }
    },
}));
