import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiX, FiClock, FiRepeat, FiTrash2 } from 'react-icons/fi';
import clsx from 'clsx';
import { Routine } from '../../types/planner';

interface RoutineModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSave: (routine: Omit<Routine, 'id'> | Partial<Routine>) => void;
    onDelete?: (id: string) => void;
    initialData?: Routine;
}

export default function RoutineModal({ isOpen, onClose, onSave, onDelete, initialData }: RoutineModalProps) {
    const [title, setTitle] = useState('');
    const [startTime, setStartTime] = useState('');
    const [duration, setDuration] = useState('');

    useEffect(() => {
        if (isOpen) {
            if (initialData) {
                setTitle(initialData.title);
                setStartTime(initialData.startTime);
                setDuration(initialData.duration);
            } else {
                setTitle('');
                setStartTime('08:00');
                setDuration('30m');
            }
        }
    }, [isOpen, initialData]);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();

        // Simple next run calculation logic for demo
        // In real app, this would be more robust
        const now = new Date();
        const [hours, minutes] = startTime.split(':').map(Number);
        const runDate = new Date();
        runDate.setHours(hours, minutes, 0, 0);

        let nextRun = '';
        if (runDate > now) {
            nextRun = `Today, ${runDate.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })}`;
        } else {
            nextRun = `Tomorrow, ${runDate.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })}`;
        }

        const routineData = {
            title,
            startTime,
            duration,
            nextRun,
            // Default icon for now, could add picker later
            icon: initialData?.icon || 'FiActivity'
        };
        onSave(routineData);
        onClose();
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
                                        className="w-full px-4 py-2 rounded-xl border border-gray-200 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 outline-none transition-all"
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
                                                value={startTime}
                                                onChange={(e) => setStartTime(e.target.value)}
                                                className="w-full pl-10 pr-4 py-2 rounded-xl border border-gray-200 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 outline-none transition-all"
                                                required
                                            />
                                        </div>
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">Duration</label>
                                        <div className="relative">
                                            <FiRepeat className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={16} />
                                            <input
                                                type="text"
                                                value={duration}
                                                onChange={(e) => setDuration(e.target.value)}
                                                className="w-full pl-10 pr-4 py-2 rounded-xl border border-gray-200 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 outline-none transition-all"
                                                placeholder="e.g. 45m"
                                                required
                                            />
                                        </div>
                                    </div>
                                </div>

                                {/* Actions */}
                                <div className="flex items-center justify-between pt-4 border-t border-gray-50">
                                    {initialData ? (
                                        <button
                                            type="button"
                                            onClick={handleDelete}
                                            className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-rose-600 hover:bg-rose-50 rounded-xl transition-colors"
                                        >
                                            <FiTrash2 size={16} />
                                            Delete Routine
                                        </button>
                                    ) : (
                                        <div></div> // Spacer
                                    )}

                                    <div className="flex items-center gap-3">
                                        <button
                                            type="button"
                                            onClick={onClose}
                                            className="px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-800 transition-colors"
                                        >
                                            Cancel
                                        </button>
                                        <button
                                            type="submit"
                                            className="px-6 py-2 bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium rounded-xl shadow-sm shadow-primary-200 transition-all active:scale-95"
                                        >
                                            {initialData ? 'Update' : 'Save'}
                                        </button>
                                    </div>
                                </div>
                            </form>
                        </div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
}
