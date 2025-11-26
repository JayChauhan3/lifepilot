import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiX, FiClock, FiRepeat, FiTrash2, FiAlertCircle } from 'react-icons/fi';
import clsx from 'clsx';
import { Routine } from '../../types/planner';
import { plannerService } from '../../services/plannerService';

// Convert 24h time string to 12h format (e.g., '13:30' -> '1:30 PM')
const to12Hour = (time24: string): string => {
    if (!time24) return '';

    const [hours, minutes] = time24.split(':').map(Number);
    const period = hours >= 12 ? 'PM' : 'AM';
    const hours12 = hours % 12 || 12;

    return `${hours12}:${minutes.toString().padStart(2, '0')} ${period}`;
};

// Convert 12h time string to 24h format (e.g., '1:30 PM' -> '13:30')
const to24Hour = (time12: string): string => {
    if (!time12) return '';

    const [time, period] = time12.split(' ');
    let [hours, minutes] = time.split(':').map(Number);

    if (period === 'PM' && hours < 12) {
        hours += 12;
    } else if (period === 'AM' && hours === 12) {
        hours = 0;
    }

    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
};

// Format time for input[type="time"] (24h format)
const formatForTimeInput = (time12: string): string => {
    if (!time12) return '';
    return to24Hour(time12);
};

// Parse time from input[type="time"] (24h format) to 12h format
const parseFromTimeInput = (time24: string): string => {
    if (!time24) return '';
    return to12Hour(time24);
};

interface RoutineModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSave: (routine: Omit<Routine, 'id'> | Partial<Routine>) => void;
    onDelete?: (id: string) => void;
    initialData?: Routine;
}

export default function RoutineModal({ isOpen, onClose, onSave, onDelete, initialData }: RoutineModalProps) {
    const [title, setTitle] = useState(initialData?.title || '');
    const [startTime, setStartTime] = useState(initialData?.startTime || '6:00 AM');
    const [endTime, setEndTime] = useState(initialData?.endTime || '10:00 AM');
    const [duration, setDuration] = useState(initialData?.duration || '4h');
    const [conflictWarning, setConflictWarning] = useState<string | null>(null);
    const [isCheckingConflict, setIsCheckingConflict] = useState(false);
    const [saveError, setSaveError] = useState<string | null>(null);

    // Update state when initialData changes
    useEffect(() => {
        if (isOpen) {
            if (initialData) {
                setTitle(initialData.title || '');
                setStartTime(initialData.startTime || '');
                setEndTime(initialData.endTime || '');
                setDuration(initialData.duration || '');
            } else {
                // Default values for new routine - ALL EMPTY
                setTitle('');
                setStartTime('');
                setEndTime('');
                setDuration('');
            }
            setConflictWarning(null);
            setSaveError(null);
        }
    }, [isOpen, initialData]);

    // Check for time conflicts whenever times change
    useEffect(() => {
        const checkConflicts = async () => {
            if (!startTime || !endTime || !isOpen) {
                return;
            }

            setIsCheckingConflict(true);
            try {
                const conflicts = await plannerService.checkTimeConflicts(
                    startTime,
                    endTime,
                    initialData?.id
                );

                if (conflicts.length > 0) {
                    const conflictRoutine = conflicts[0];
                    const warningMsg = `Time conflict with "${conflictRoutine.title}" (${conflictRoutine.startTime} - ${conflictRoutine.endTime})`;
                    setConflictWarning(warningMsg);
                } else {
                    setConflictWarning(null);
                }
            } catch (error) {
                console.error('❌ Failed to check conflicts:', error);
                // Don't show error to user for conflict check failures
            } finally {
                setIsCheckingConflict(false);
            }
        };

        // Debounce the conflict check
        const timeoutId = setTimeout(checkConflicts, 300);
        return () => clearTimeout(timeoutId);
    }, [startTime, endTime, isOpen, initialData?.id]);

    // Calculate duration in minutes between start and end time (both in 12h format)
    const calculateDuration = (start12h: string, end12h: string): string => {
        if (!start12h || !end12h) return '0m';

        // Convert to 24h for calculation
        const start24h = to24Hour(start12h);
        const end24h = to24Hour(end12h);

        const [startHours, startMins] = start24h.split(':').map(Number);
        const [endHours, endMins] = end24h.split(':').map(Number);

        let totalMinutes = (endHours * 60 + endMins) - (startHours * 60 + startMins);

        // Handle overnight case
        if (totalMinutes < 0) {
            totalMinutes += 24 * 60;
        }

        // Return in format "1h 30m" or "45m"
        const hours = Math.floor(totalMinutes / 60);
        const minutes = totalMinutes % 60;

        if (hours > 0) {
            return minutes > 0 ? `${hours}h ${minutes}m` : `${hours}h`;
        }
        return `${minutes}m`;
    };

    // Calculate end time based on start time (12h) and duration
    const calculateEndTime = (start12h: string | undefined, duration: string): string => {
        if (!start12h) return '9:00 AM'; // Default end time if start is not provided

        // Convert start time to 24h for calculation
        const start24h = to24Hour(start12h);
        let [hours, minutes] = start24h.split(':').map(Number);
        let totalMinutes = hours * 60 + minutes;

        // Parse duration (e.g., "1h 30m" or "45m")
        const hourMatch = duration.match(/(\d+)h/);
        const minMatch = duration.match(/(\d+)m/);

        if (hourMatch) totalMinutes += parseInt(hourMatch[1]) * 60;
        if (minMatch) totalMinutes += parseInt(minMatch[1]);

        // Handle overflow to next day
        totalMinutes = totalMinutes % (24 * 60);

        // Convert back to 12h format
        const endHours = Math.floor(totalMinutes / 60);
        const endMins = totalMinutes % 60;
        const period = endHours >= 12 ? 'PM' : 'AM';
        const displayHours = endHours % 12 || 12;

        return `${displayHours}:${endMins.toString().padStart(2, '0')} ${period}`;
    };

    const handleStartTimeChange = (time24: string) => {
        // Convert from 24h input to 12h format for storage
        const newStartTime = parseFromTimeInput(time24);
        setStartTime(newStartTime);

        // Update duration when start time changes
        setDuration(calculateDuration(newStartTime, endTime));
    };

    const handleEndTimeChange = (time24: string) => {
        // Convert from 24h input to 12h format for storage
        const newEndTime = parseFromTimeInput(time24);
        setEndTime(newEndTime);

        // Update duration when end time changes
        setDuration(calculateDuration(startTime, newEndTime));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setSaveError(null);

        // Simple next run calculation logic for demo
        const now = new Date();
        const start24h = to24Hour(startTime);
        const [hours, minutes] = start24h.split(':').map(Number);

        const runDate = new Date();
        runDate.setHours(hours, minutes, 0, 0);

        let nextRun = '';
        if (runDate > now) {
            nextRun = `Today, ${startTime}`;
        } else {
            // If the time has passed for today, schedule for tomorrow
            const tomorrow = new Date();
            tomorrow.setDate(tomorrow.getDate() + 1);
            tomorrow.setHours(hours, minutes, 0, 0);
            nextRun = `Tomorrow, ${startTime}`;
        }

        const routineData = {
            title,
            startTime,  // Already in 12h format
            endTime,    // Already in 12h format
            duration,
            nextRun,
            // Default icon for now, could add picker later
            icon: initialData?.icon || 'FiActivity',
            // Ensure we're not sending internal fields to the backend
            _time_of_day: undefined,
            _end_time: undefined
        };

        try {
            await onSave(routineData);
            onClose();
        } catch (error: any) {
            // Show error message from backend
            setSaveError(error.message || 'Failed to save routine');
        }
    };

    const handleDelete = () => {
        if (initialData && onDelete) {
            onDelete(initialData.id);
            onClose();
        }
    }

    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="fixed inset-0 bg-black/20 backdrop-blur-sm z-50"
                    />
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: 20 }}
                        className="fixed inset-0 m-auto w-full max-w-md h-fit bg-white rounded-2xl shadow-xl z-50 overflow-hidden"
                    >
                        <div className="p-6">
                            <div className="flex items-center justify-between mb-6">
                                <h2 className="text-lg font-bold text-gray-900">
                                    {initialData ? 'Edit Routine' : 'Create New Routine'}
                                </h2>
                                <button onClick={onClose} className="text-gray-400 hover:text-gray-600 transition-colors">
                                    <FiX size={20} />
                                </button>
                            </div>

                            <form onSubmit={handleSubmit} className="space-y-4">
                                {/* Title */}
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Routine Title</label>
                                    <input
                                        type="text"
                                        value={title}
                                        onChange={(e) => setTitle(e.target.value)}
                                        disabled={initialData?.canEditTitle === false}
                                        className={clsx(
                                            "w-full px-4 py-2 rounded-xl border border-gray-200 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 outline-none transition-all text-black",
                                            initialData?.canEditTitle === false && "bg-gray-100 text-gray-500 cursor-not-allowed"
                                        )}
                                        placeholder="e.g. Morning Workout"
                                        required
                                    />
                                </div>

                                {/* Time & Duration */}
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">Start Time</label>
                                        <div className="relative">
                                            <FiClock className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={16} />
                                            <input
                                                type="time"
                                                value={formatForTimeInput(startTime) || ''}
                                                onChange={(e) => handleStartTimeChange(e.target.value)}
                                                className="w-full pl-10 pr-4 py-2 rounded-xl border border-gray-200 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 outline-none transition-all text-black"
                                                required
                                            />
                                        </div>
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">End Time</label>
                                        <div className="relative">
                                            <FiClock className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={16} />
                                            <input
                                                type="time"
                                                value={formatForTimeInput(endTime) || ''}
                                                onChange={(e) => handleEndTimeChange(e.target.value)}
                                                className="w-full pl-10 pr-4 py-2 rounded-xl border border-gray-200 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 outline-none transition-all text-black"
                                                required
                                            />
                                        </div>
                                    </div>
                                </div>

                                {/* Conflict Warning */}
                                {conflictWarning && (
                                    <motion.div
                                        initial={{ opacity: 0, y: -10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        className="flex items-start gap-2 p-3 bg-red-50 border border-red-200 rounded-xl"
                                    >
                                        <FiAlertCircle className="text-red-600 flex-shrink-0 mt-0.5" size={16} />
                                        <p className="text-sm text-red-700">{conflictWarning}</p>
                                    </motion.div>
                                )}

                                {/* Save Error */}
                                {saveError && (
                                    <motion.div
                                        initial={{ opacity: 0, y: -10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        className="flex items-start gap-2 p-3 bg-red-50 border border-red-200 rounded-xl"
                                    >
                                        <FiAlertCircle className="text-red-600 flex-shrink-0 mt-0.5" size={16} />
                                        <p className="text-sm text-red-700">{saveError}</p>
                                    </motion.div>
                                )}

                                {/* Duration (read-only) */}
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Duration</label>
                                    <div className="relative">
                                        <FiRepeat className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={16} />
                                        <input
                                            type="text"
                                            value={duration}
                                            readOnly
                                            className="w-full pl-10 pr-4 py-2 rounded-xl border border-gray-200 bg-gray-50 text-black outline-none"
                                        />
                                    </div>
                                </div>

                                {/* Actions */}
                                <div className="flex items-center justify-end pt-4 border-t border-gray-50 gap-3">
                                    <button
                                        type="button"
                                        onClick={onClose}
                                        className="px-4 py-2 text-sm font-medium text-black hover:text-gray-800 transition-colors"
                                    >
                                        Cancel
                                    </button>
                                    <button
                                        type="submit"
                                        disabled={!!conflictWarning || isCheckingConflict || !startTime || !endTime || !title}
                                        className={clsx(
                                            "px-6 py-2 text-sm font-medium rounded-xl shadow-sm transition-all active:scale-95",
                                            (conflictWarning || isCheckingConflict || !startTime || !endTime || !title)
                                                ? "bg-gray-300 text-gray-500 cursor-not-allowed"
                                                : "bg-primary-600 hover:bg-primary-700 text-white shadow-primary-200"
                                        )}
                                    >
                                        {isCheckingConflict ? 'Checking...' : (initialData ? 'Update' : 'Save')}
                                    </button>
                                </div>
                            </form>
                        </div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
}
