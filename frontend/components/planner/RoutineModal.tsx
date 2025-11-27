import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  FiX,
  FiClock,
  FiRepeat,
  FiTrash2,
  FiAlertCircle,
  FiBriefcase,
  FiSun,
  FiMoon,
  FiCoffee,
  FiActivity
} from 'react-icons/fi';
import clsx from 'clsx';
import { Routine } from '../../types/planner';
import { plannerService } from '../../services/plannerService';

// Default routine IDs
export const WORK_BLOCK_ID = 'WORK_BLOCK_DEFAULT_ID';
export const MORNING_ROUTINE_ID = 'MORNING_ROUTINE_DEFAULT_ID';
export const EVENING_ROUTINE_ID = 'EVENING_ROUTINE_DEFAULT_ID';
export const SLEEP_ROUTINE_ID = 'SLEEP_ROUTINE_DEFAULT_ID';

// Default routine icons
const ROUTINE_ICONS: Record<string, any> = {
  [WORK_BLOCK_ID]: FiBriefcase,
  [MORNING_ROUTINE_ID]: FiSun,
  [EVENING_ROUTINE_ID]: FiMoon,
  [SLEEP_ROUTINE_ID]: FiMoon,
  default: FiActivity
};

// Default routine configurations
const DEFAULT_ROUTINES = {
  [WORK_BLOCK_ID]: {
    title: 'Work Block',
    icon: FiBriefcase,
    isProtected: true,
    canDelete: false,
    canEditTitle: false,
    canEditTime: true
  },
  [MORNING_ROUTINE_ID]: {
    title: 'Morning Routine',
    icon: 'FiSun',
    isProtected: false,
    canDelete: true,
    canEditTitle: true,
    canEditTime: true
  },
  [EVENING_ROUTINE_ID]: {
    title: 'Evening Routine',
    icon: 'FiMoon',
    isProtected: false,
    canDelete: true,
    canEditTitle: true,
    canEditTime: true
  },
  [SLEEP_ROUTINE_ID]: {
    title: 'Sleep',
    icon: 'FiMoon',
    isProtected: false,
    canDelete: true,
    canEditTitle: true,
    canEditTime: true
  }
};

// Convert 24h time string to 12h format (e.g., '13:30' -> '1:30 PM')
const to12Hour = (time24: string): string => {
  if (!time24) return '';

  const [hours, minutes] = time24.split(':').map(Number);
  const period = hours >= 12 ? 'PM' : 'AM';
  const hours12 = hours % 12 || 12;

  return `${hours12}:${minutes.toString().padStart(2, '0')} ${period}`;
};

// Convert 12h time string to 24h format (e.g., '1:30 PM' -> '13:30')
const to24Hour = (time12h: string | undefined): string => {
  if (!time12h || time12h === '--:--') {
    console.warn('No time provided to to24Hour');
    return '00:00';
  }

  try {
    // Handle already 24h format (e.g., '13:30' or '06:00')
    if (/^\d{1,2}:\d{2}$/.test(time12h) && !time12h.includes(' ')) {
      // Ensure it's padded to HH:MM format
      const [h, m] = time12h.split(':');
      return `${h.padStart(2, '0')}:${m}`;
    }

    const time = time12h.trim();

    // Handle NaN in time string
    if (time.includes('NaN')) {
      console.warn('Invalid time format - contains NaN, using default 12:00');
      return '12:00';
    }

    // Extract time and period parts
    const [timePart, period] = time.split(' ');
    if (!timePart || !period) {
      console.warn('Invalid time format - missing time or period, using default 12:00');
      return '12:00';
    }

    // Split hours and minutes
    const [hoursStr, minutesStr = '00'] = timePart.split(':');

    // Parse hours and minutes with validation
    const hours = Math.min(12, Math.max(1, parseInt(hoursStr, 10) || 12));
    const minutes = Math.min(59, Math.max(0, parseInt(minutesStr, 10) || 0));

    // Convert to 24-hour format
    const periodUpper = period.toUpperCase();
    let hours24 = hours;

    if (periodUpper === 'PM' && hours < 12) {
      hours24 = hours + 12;
    } else if (periodUpper === 'AM' && hours === 12) {
      hours24 = 0;
    }

    return `${hours24.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
  } catch (error) {
    console.error('Error converting time to 24h format, using default 12:00:', error);
    return '12:00';
  }
};

// Format time for input[type="time"] (24h format)
const formatForTimeInput = (time: string): string => {
  if (!time) return '';

  // If already in 24h format (HH:MM), return as is
  if (/^\d{1,2}:\d{2}$/.test(time) && !time.includes(' ')) {
    return time;
  }

  // Convert 12h to 24h format
  try {
    let [timePart, period] = time.split(' ');
    let [hours, minutes] = timePart.split(':').map(Number);

    if (period === 'PM' && hours < 12) {
      hours += 12;
    } else if (period === 'AM' && hours === 12) {
      hours = 0;
    }

    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
  } catch (error) {
    console.error('Error formatting time for input:', error);
    return '';
  }
};

// Parse time from input[type="time"] (24h format) to 12h format
const parseFromTimeInput = (time24: string): string => {
  if (!time24) return '';

  try {
    let [hours, minutes] = time24.split(':').map(Number);
    let period = 'AM';

    if (hours >= 12) {
      period = 'PM';
      if (hours > 12) hours -= 12;
    } else if (hours === 0) {
      hours = 12;
    }

    return `${hours}:${minutes.toString().padStart(2, '0')} ${period}`;
  } catch (error) {
    console.error('Error parsing time from input:', error);
    return '';
  }
};

interface RoutineModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (routine: Omit<Routine, 'id'> | Partial<Routine>) => Promise<void>;
  initialData?: Routine | null;
  isDefaultWorkBlock?: boolean;
  existingRoutines?: Routine[];
}

export default function RoutineModal({
  isOpen,
  onClose,
  onSave,
  initialData = null,
  isDefaultWorkBlock = false,
  existingRoutines = []
}: RoutineModalProps) {
  const isEditing = !!initialData?.id;
  const isWorkBlock = isDefaultWorkBlock || initialData?.id === WORK_BLOCK_ID;

  // Determine if this is a protected routine (default work block or other protected routines)
  const isProtected = isWorkBlock || initialData?.isProtected === true;

  // Determine if the title can be edited
  const canEditTitle = !isProtected || (initialData?.canEditTitle ?? true);

  // State for form fields
  const [title, setTitle] = useState('');
  const [startTime, setStartTime] = useState('');
  const [endTime, setEndTime] = useState('');
  const [duration, setDuration] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [conflictError, setConflictError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Initialize form with default values or initialData
  useEffect(() => {
    if (isOpen) {
      if (initialData) {
        // Set title from initialData
        setTitle(initialData.title || '');

        // Times are already in 12h format from the service layer (e.g., "6:00 AM")
        // No need to convert them again
        setStartTime(initialData.startTime || '9:00 AM');
        setEndTime(initialData.endTime || '5:00 PM');

        setDuration(initialData.duration || '');
      } else {
        // For new routines, set default times based on the type
        if (isDefaultWorkBlock || isWorkBlock) {
          setTitle('Work Block');
          setStartTime('10:00 AM');
          setEndTime('5:00 PM');
        } else {
          // Default for new routines
          setTitle('New Routine');
          setStartTime('9:00 AM');
          setEndTime('5:00 PM');
        }
        setDuration('8h');
      }
      setError(null);
      setConflictError(null);
    }
  }, [initialData, isOpen]);

  // Calculate duration when start or end time changes
  useEffect(() => {
    if (startTime && endTime) {
      const durationStr = calculateDuration(startTime, endTime);
      setDuration(durationStr);
      checkForConflicts();
    } else {
      setDuration('');
    }
  }, [startTime, endTime]);

  // Convert 12h time string to 24h format (e.g., '1:30 PM' -> '13:30')
  const to24Hour = (time12h: string): string => {
    if (!time12h) return '';

    // If already in 24h format, return as is
    if (/^\d{1,2}:\d{2}$/.test(time12h)) {
      return time12h;
    }

    const [timePart, period] = time12h.split(' ');
    if (!timePart || !period) return '';

    let [hours, minutes] = timePart.split(':').map(Number);

    if (period.toUpperCase() === 'PM' && hours < 12) {
      hours += 12;
    } else if (period.toUpperCase() === 'AM' && hours === 12) {
      hours = 0;
    }

    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
  };

  // Convert 24h time string to 12h format (e.g., '13:30' -> '1:30 PM')
  const to12Hour = (time24: string): string => {
    if (!time24) return '';

    const [hours, minutes] = time24.split(':').map(Number);
    const period = hours >= 12 ? 'PM' : 'AM';
    const hours12 = hours % 12 || 12;

    return `${hours12}:${minutes.toString().padStart(2, '0')} ${period}`;
  };

  // Format time for time input (HH:MM)
  const formatForTimeInput = (time12: string): string => {
    return to24Hour(time12) || '';
  };

  // Parse time from time input (HH:MM) to 12h format
  const parseFromTimeInput = (time24: string): string => {
    return to12Hour(time24) || '';
  };

  // Calculate duration between two times
  const calculateDuration = (start: string, end: string): string => {
    if (!start || !end) return '0m';

    try {
      const start24h = to24Hour(start);
      const end24h = to24Hour(end);

      if (!start24h || !end24h) return '0m';

      const [startHours, startMins] = start24h.split(':').map(Number);
      const [endHours, endMins] = end24h.split(':').map(Number);

      let totalMinutes = (endHours * 60 + endMins) - (startHours * 60 + startMins);

      // Handle overnight
      if (totalMinutes < 0) {
        totalMinutes += 24 * 60;
      }

      const hours = Math.floor(totalMinutes / 60);
      const minutes = totalMinutes % 60;

      if (hours > 0) {
        return minutes > 0 ? `${hours}h ${minutes}m` : `${hours}h`;
      }
      return `${minutes}m`;
    } catch (error) {
      console.error('Error calculating duration:', error);
      return '0m';
    }
  };
  // Check for time conflicts with other routines
  const checkForConflicts = useCallback(async () => {
    if (!startTime || !endTime || !title.trim()) {
      return false;
    }

    try {
      // Convert to 24h format for comparison
      let start24h = startTime;
      let end24h = endTime;

      // If time includes AM/PM, convert to 24h format
      if (startTime.includes(' ') || startTime.includes('AM') || startTime.includes('PM')) {
        start24h = to24Hour(startTime);
      }
      if (endTime.includes(' ') || endTime.includes('AM') || endTime.includes('PM')) {
        end24h = to24Hour(endTime);
      }

      // Ensure times are in HH:MM format
      if (!/^\d{1,2}:\d{2}$/.test(start24h) || !/^\d{1,2}:\d{2}$/.test(end24h)) {
        setConflictError('Invalid time format');
        return false;
      }

      if (!start24h || !end24h) {
        setConflictError('Invalid time format');
        return false;
      }

      // Check if end time is after start time
      if (start24h >= end24h) {
        setConflictError('End time must be after start time');
        return false;
      }

      // Check for conflicts with existing routines
      const conflicts = await plannerService.checkTimeConflicts(
        start24h,
        end24h,
        initialData?.id
      );

      if (conflicts.length > 0) {
        const conflictNames = conflicts.map(c => c.title).join(', ');
        setConflictError(`This time conflicts with: ${conflictNames}`);
        return false;
      }

      setConflictError(null);
      return false;
    } catch (error) {
      console.error('Error checking for conflicts:', error);
      return false;
    }
  }, [startTime, endTime, title, initialData?.id]);

  // Check for conflicts when times change
  useEffect(() => {
    if (isOpen) {
      checkForConflicts();
    }
  }, [startTime, endTime, isOpen, checkForConflicts]);

  // Calculate duration when start or end time changes
  useEffect(() => {
    if (startTime && endTime) {
      try {
        const start24h = to24Hour(startTime);
        const end24h = to24Hour(endTime);

        if (start24h && end24h) {
          const [startHours, startMins] = start24h.split(':').map(Number);
          const [endHours, endMins] = end24h.split(':').map(Number);

          let totalMinutes = (endHours * 60 + endMins) - (startHours * 60 + startMins);

          // Handle overnight case
          if (totalMinutes < 0) {
            totalMinutes += 24 * 60;
          }

          // Set duration in format "1h 30m" or "45m"
          const hours = Math.floor(totalMinutes / 60);
          const minutes = totalMinutes % 60;

          if (hours > 0) {
            setDuration(minutes > 0 ? `${hours}h ${minutes}m` : `${hours}h`);
          } else {
            setDuration(`${minutes}m`);
          }
        }
      } catch (error) {
        console.error('Error calculating duration:', error);
        setDuration('0m');
      }
    }
  }, [startTime, endTime]);

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (isSubmitting) return;

    // Basic validation
    if (!title.trim()) {
      setError('Please enter a title');
      return;
    }

    if (!startTime || !endTime) {
      setError('Please set both start and end times');
      return;
    }

    // Convert times to 24-hour format for backend
    const formattedStartTime = to24Hour(startTime);
    const formattedEndTime = to24Hour(endTime);

    // Check for time conflicts
    const hasConflicts = await checkForConflicts();
    if (hasConflicts) {
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      // Prepare routine data
      const routineData: Partial<Routine> = {
        ...(initialData || {}),
        title: title.trim(),
        startTime,
        endTime,
        duration,
        isWorkBlock: isWorkBlock,
        isProtected: isProtected,
        canEditTitle: canEditTitle,
        canEditTime: true
      };

      await onSave(routineData);
      onClose();
    } catch (error) {
      console.error('Error saving routine:', error);
      setError('Failed to save routine. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };


  if (!isOpen) return null;

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="relative bg-white rounded-lg shadow-xl w-full max-w-md max-h-[90vh] overflow-y-auto"
          >
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900">
                  {initialData ? 'Edit Routine' : 'Create New Routine'}
                </h2>
                <button
                  onClick={onClose}
                  className="text-gray-400 hover:text-gray-500"
                  disabled={isSubmitting}
                >
                  <FiX className="h-6 w-6" />
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
                    placeholder="Routine name"
                    disabled={!canEditTitle}
                    className={`w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-black placeholder-gray-500 ${!canEditTitle ? 'bg-gray-100 cursor-not-allowed text-gray-700' : ''
                      }`}
                  />
                </div>

                {/* Time & Duration */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Start Time
                    </label>
                    <input
                      type="time"
                      value={to24Hour(startTime) || '09:00'}
                      onChange={(e) => setStartTime(to12Hour(e.target.value) || '9:00 AM')}
                      className="w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-black"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      End Time
                    </label>
                    <input
                      type="time"
                      value={to24Hour(endTime) || '17:00'}
                      onChange={(e) => setEndTime(to12Hour(e.target.value) || '5:00 PM')}
                      className="w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-black"
                    />
                  </div>
                </div>

                {/* Duration Display */}
                <div className="text-sm text-gray-600">
                  Duration: {duration || '0h 0m'}
                </div>

                {/* Error Message */}
                {error && (
                  <div className="text-red-500 text-sm mt-2">
                    {error}
                  </div>
                )}

                {/* Form Actions */}
                <div className="flex space-x-3">
                  <button
                    type="button"
                    onClick={onClose}
                    disabled={isSubmitting}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={isSubmitting || !!conflictError}
                    className={`px-4 py-2 text-sm font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${isSubmitting || conflictError
                      ? 'bg-gray-300 text-gray-600 cursor-not-allowed'
                      : 'bg-blue-600 hover:bg-blue-700 text-white shadow-sm'
                      }`}
                  >
                    {isSubmitting ? 'Saving...' : (initialData ? 'Update' : 'Save')}
                  </button>
                </div>
              </form>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
