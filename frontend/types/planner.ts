export type TaskType = 'today' | 'upcoming' | 'done';

export interface Task {
    id: string;
    title: string;
    tags: string[];
    aim: string;
    date: string; // YYYY-MM-DD
    time: string; // HH:mm
    isCompleted: boolean;
    type: TaskType;
}

export interface Routine {
    id: string;
    title: string;
    startTime: string; // HH:mm
    endTime: string;   // HH:mm
    duration: string;  // e.g. "45m" or "2h"
    nextRun: string;   // calculated string
    icon?: string;     // Optional icon name or identifier
    isWorkBlock?: boolean; // Identifies work block routines
}
