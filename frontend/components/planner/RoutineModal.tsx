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
        // Handle already 24h format (e.g., '13:30')
        if (/^\d{1,2}:\d{2}$/.test(time12h)) {
            return time12h;
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
  onSave: (routine: Omit<Routine, 'id'> | Partial<Routine>) => Promise<void>;
  onDelete?: (id: string) => Promise<void>;
  initialData?: Routine | null;
  isDefaultWorkBlock?: boolean;
  existingRoutines?: Routine[];
}

export default function RoutineModal({ 
  isOpen, 
  onClose, 
  onSave, 
  onDelete, 
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
  
  // Determine if the routine can be deleted
  const canDelete = !isProtected && (initialData?.canDelete ?? true);
  
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
        setTitle(initialData.title || '');
        setStartTime(initialData.startTime || '');
        setEndTime(initialData.endTime || '');
        setDuration(initialData.duration || '');
      } else {
        // For new routines, don't set any default values
        setTitle('');
        setStartTime('');
        setEndTime('');
        setDuration('');
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
    
    // Validate form
    if (!title.trim()) {
      setError('Please enter a title');
      return;
    }
    
    if (!startTime || !endTime) {
      setError('Please set both start and end times');
      return;
    }
    
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
        canDelete: canDelete,
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

  // Handle delete routine
  const handleDelete = async () => {
    if (isSubmitting || !onDelete || !initialData?.id) return;
    
    if (isProtected) {
      setError('This routine cannot be deleted');
      return;
    }

    if (window.confirm(`Are you sure you want to delete "${title}"?`)) {
      setIsSubmitting(true);
      setError(null);
      
      try {
        await onDelete(initialData.id);
        onClose();
      } catch (error) {
        console.error('Error deleting routine:', error);
        setError('Failed to delete routine. Please try again.');
      } finally {
        setIsSubmitting(false);
      }
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
                            className={`w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                                !canEditTitle ? 'bg-gray-100 cursor-not-allowed' : ''
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
                                value={formatForTimeInput(startTime)}
                                onChange={(e) => setStartTime(parseFromTimeInput(e.target.value))}
                                disabled={isSubmitting}
                                className="w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                End Time
                            </label>
                            <input
                                type="time"
                                value={formatForTimeInput(endTime)}
                                onChange={(e) => setEndTime(parseFromTimeInput(e.target.value))}
                                disabled={isSubmitting}
                                className="w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
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
                    <div className="flex justify-end space-x-3 pt-4 border-t mt-6">
                        {onDelete && initialData && canDelete && (
                            <button
                                type="button"
                                onClick={handleDelete}
                                disabled={isSubmitting}
                                className="px-4 py-2 text-sm font-medium text-red-600 hover:bg-red-50 rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                Delete
                            </button>
                        )}
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
                            className={`px-4 py-2 text-sm font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${
                                isSubmitting || conflictError
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
