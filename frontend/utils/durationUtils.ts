import { Task } from '../types/planner';

/**
 * Parse duration string (e.g., "1h 30m", "45m", "2h") to total minutes
 */
export function parseDurationToMinutes(duration: string): number {
    if (!duration) return 0;

    let totalMinutes = 0;

    // Match hours (e.g., "1h", "2h")
    const hoursMatch = duration.match(/(\d+)h/);
    if (hoursMatch) {
        totalMinutes += parseInt(hoursMatch[1], 10) * 60;
    }

    // Match minutes (e.g., "30m", "45m")
    const minutesMatch = duration.match(/(\d+)m/);
    if (minutesMatch) {
        totalMinutes += parseInt(minutesMatch[1], 10);
    }

    return totalMinutes;
}

/**
 * Format minutes to duration string (e.g., 90 -> "1h 30m", 45 -> "45m")
 */
export function formatMinutesToDuration(minutes: number): string {
    if (minutes === 0) return '0m';

    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;

    let result = '';
    if (hours > 0) result += `${hours}h`;
    if (mins > 0) result += ` ${mins}m`;

    return result.trim();
}

/**
 * Calculate total duration in minutes for an array of tasks
 */
export function calculateTotalDuration(tasks: Task[]): number {
    return tasks.reduce((total, task) => {
        return total + parseDurationToMinutes(task.duration);
    }, 0);
}

/**
 * Format duration for display (handles both single units and combinations)
 */
export function formatDurationForDisplay(minutes: number): string {
    if (minutes === 0) return '0 minutes';

    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;

    const parts: string[] = [];
    if (hours > 0) parts.push(`${hours}hr${hours > 1 ? 's' : ''}`);
    if (mins > 0) parts.push(`${mins}min${mins > 1 ? 's' : ''}`);

    return parts.join(' ');
}
