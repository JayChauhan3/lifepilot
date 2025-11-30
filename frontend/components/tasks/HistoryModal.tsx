import { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiX, FiCalendar, FiClock, FiCheckCircle } from 'react-icons/fi';
import { usePlannerStore } from '../../store/plannerStore';
import { format } from 'date-fns';

interface HistoryModalProps {
    isOpen: boolean;
    onClose: () => void;
}

export default function HistoryModal({ isOpen, onClose }: HistoryModalProps) {
    const { historyTasks, fetchTaskHistory, isLoading } = usePlannerStore();

    useEffect(() => {
        if (isOpen) {
            fetchTaskHistory();
        }
    }, [isOpen, fetchTaskHistory]);

    // Group tasks by date
    const groupedTasks = historyTasks.reduce((acc, task) => {
        const date = task.date || 'Unknown Date';
        if (!acc[date]) {
            acc[date] = [];
        }
        acc[date].push(task);
        return acc;
    }, {} as Record<string, typeof historyTasks>);

    // Sort dates descending
    const sortedDates = Object.keys(groupedTasks).sort((a, b) =>
        new Date(b).getTime() - new Date(a).getTime()
    );

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
                        className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-2xl bg-white rounded-2xl shadow-xl z-50 max-h-[80vh] flex flex-col overflow-hidden"
                    >
                        <div className="flex items-center justify-between p-6 border-b border-gray-100">
                            <div className="flex items-center gap-3">
                                <div className="p-2 bg-primary-50 text-primary-600 rounded-xl">
                                    <FiClock size={24} />
                                </div>
                                <div>
                                    <h2 className="text-xl font-bold text-gray-900">Task History</h2>
                                    <p className="text-sm text-gray-500">Archived completed tasks</p>
                                </div>
                            </div>
                            <button
                                onClick={onClose}
                                className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-50 rounded-lg transition-colors"
                            >
                                <FiX size={20} />
                            </button>
                        </div>

                        <div className="flex-1 overflow-y-auto p-6 custom-scrollbar">
                            {isLoading ? (
                                <div className="flex items-center justify-center py-12">
                                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
                                </div>
                            ) : historyTasks.length === 0 ? (
                                <div className="text-center py-12 text-gray-400">
                                    <FiClock size={48} className="mx-auto mb-4 opacity-20" />
                                    <p>No archived tasks found</p>
                                </div>
                            ) : (
                                <div className="space-y-8">
                                    {sortedDates.map(date => (
                                        <div key={date}>
                                            <div className="flex items-center gap-2 mb-4">
                                                <FiCalendar className="text-gray-400" />
                                                <h3 className="font-semibold text-gray-700">
                                                    {format(new Date(date), 'MMMM d, yyyy')}
                                                </h3>
                                                <span className="text-xs text-gray-400 bg-gray-100 px-2 py-0.5 rounded-full">
                                                    {groupedTasks[date].length} tasks
                                                </span>
                                            </div>
                                            <div className="space-y-2">
                                                {groupedTasks[date].map(task => (
                                                    <div
                                                        key={task.id}
                                                        className="flex items-center justify-between p-3 bg-gray-50 rounded-xl border border-gray-100"
                                                    >
                                                        <div className="flex items-center gap-3">
                                                            <FiCheckCircle className="text-green-500 shrink-0" />
                                                            <span className="text-gray-600 line-through">{task.title}</span>
                                                        </div>
                                                        <div className="flex items-center gap-3">
                                                            {task.tags?.map(tag => (
                                                                <span key={tag} className="text-[10px] uppercase font-medium text-gray-500 bg-white px-2 py-1 rounded border border-gray-200">
                                                                    {tag}
                                                                </span>
                                                            ))}
                                                            <span className="text-xs text-gray-400 font-mono">
                                                                {task.duration}
                                                            </span>
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
}
