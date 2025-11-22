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
            // Initialize with some dummy data if empty for demo purposes, matching the user request
            if (tasks.length === 0) {
                const dummyTasks: Task[] = [
                    { id: '1', title: "Review Q3 Marketing Plan", tags: ["Work"], aim: "Review the Q3 plan", date: new Date().toISOString().split('T')[0], time: "09:00", isCompleted: false, type: 'today' },
                    { id: '2', title: "Call with Design Team", tags: ["Meeting"], aim: "Discuss new designs", date: new Date().toISOString().split('T')[0], time: "14:00", isCompleted: false, type: 'today' },
                    { id: '3', title: "Buy Groceries", tags: ["Personal"], aim: "Milk, eggs, bread", date: new Date().toISOString().split('T')[0], time: "17:30", isCompleted: false, type: 'today' },
                    { id: '4', title: "Update Website Copy", tags: ["Project"], aim: "Update homepage copy", date: "2025-11-24", time: "10:00", isCompleted: false, type: 'upcoming' },
                    { id: '5', title: "Prepare Monthly Report", tags: ["Admin"], aim: "Compile stats", date: "2025-11-25", time: "11:00", isCompleted: false, type: 'upcoming' },
                    { id: '6', title: "Morning Standup", tags: ["Meeting"], aim: "Daily sync", date: new Date().toISOString().split('T')[0], time: "09:00", isCompleted: true, type: 'done' },
                ];
                set({ tasks: dummyTasks, isLoading: false });
            } else {
                set({ tasks, isLoading: false });
            }
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

        const newIsCompleted = !task.isCompleted;
        const newType = newIsCompleted ? 'done' : (task.date === new Date().toISOString().split('T')[0] ? 'today' : 'upcoming');

        await get().updateTask(id, { isCompleted: newIsCompleted, type: newType });
    },

    fetchRoutines: async () => {
        set({ isLoading: true, error: null });
        try {
            const routines = await plannerService.getRoutines();
            if (routines.length === 0) {
                const dummyRoutines: Routine[] = [
                    { id: '1', title: "Morning Routine", startTime: "08:00", duration: "45m", nextRun: "Tomorrow, 8:00 AM", icon: "FiSun" },
                    { id: '2', title: "Deep Work Block", startTime: "09:00", duration: "2h", nextRun: "Tomorrow, 9:00 AM", icon: "FiBriefcase" },
                    { id: '3', title: "Gym Workout", startTime: "17:30", duration: "1h", nextRun: "Today, 5:30 PM", icon: "FiActivity" },
                    { id: '4', title: "Evening Wind Down", startTime: "21:30", duration: "30m", nextRun: "Today, 9:30 PM", icon: "FiMoon" },
                    { id: '5', title: "Reading Time", startTime: "22:00", duration: "30m", nextRun: "Today, 10:00 PM", icon: "FiBook" },
                ];
                set({ routines: dummyRoutines, isLoading: false });
            } else {
                set({ routines, isLoading: false });
            }
        } catch (error) {
            set({ error: 'Failed to fetch routines', isLoading: false });
        }
    },

    addRoutine: async (routine) => {
        set({ isLoading: true, error: null });
        try {
            const newRoutine = await plannerService.createRoutine(routine);
            set((state) => ({ routines: [...state.routines, newRoutine], isLoading: false }));
        } catch (error) {
            set({ error: 'Failed to add routine', isLoading: false });
        }
    },

    updateRoutine: async (id, updatedFields) => {
        set({ isLoading: true, error: null });
        try {
            await plannerService.updateRoutine(id, updatedFields);
            set((state) => ({
                routines: state.routines.map((r) => (r.id === id ? { ...r, ...updatedFields } : r)),
                isLoading: false,
            }));
        } catch (error) {
            set({ error: 'Failed to update routine', isLoading: false });
        }
    },

    deleteRoutine: async (id) => {
        set({ isLoading: true, error: null });
        try {
            await plannerService.deleteRoutine(id);
            set((state) => ({
                routines: state.routines.filter((r) => r.id !== id),
                isLoading: false,
            }));
        } catch (error) {
            set({ error: 'Failed to delete routine', isLoading: false });
        }
    },
}));
