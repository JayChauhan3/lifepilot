import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiX, FiCalendar, FiClock, FiTag } from 'react-icons/fi';
import clsx from 'clsx';
import { Task, TaskType } from '../../types/planner';

interface TaskModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSave: (task: Omit<Task, 'id'> | Partial<Task>) => void;
    initialData?: Task;
    defaultType?: TaskType;
}

export default function TaskModal({ isOpen, onClose, onSave, initialData, defaultType = 'today' }: TaskModalProps) {
    const [title, setTitle] = useState('');
    const [tags, setTags] = useState<string[]>([]);
    const [tagInput, setTagInput] = useState('');
    const [aim, setAim] = useState('');
    const [date, setDate] = useState('');
    const [hours, setHours] = useState('');
    const [minutes, setMinutes] = useState('');
    const [error, setError] = useState('');
    const [type, setType] = useState<TaskType>(defaultType);

    // Helper to get local date string YYYY-MM-DD
    const getLocalDate = () => {
        const d = new Date();
        const offset = d.getTimezoneOffset() * 60000;
        return new Date(d.getTime() - offset).toISOString().split('T')[0];
    };

    useEffect(() => {
        if (isOpen) {
            if (initialData) {
                setTitle(initialData.title);
                setTags(initialData.tags);
                setAim(initialData.aim);
                setDate(initialData.date);
                // Parse duration string (e.g., "1h 30m" or "45m")
                const dur = initialData.duration || '';
                const hMatch = dur.match(/(\d+)h/);
                const mMatch = dur.match(/(\d+)m/);
                setHours(hMatch ? hMatch[1] : '');
                setMinutes(mMatch ? mMatch[1] : '');
                setError('');
                setType(initialData.type);
            } else {
                setTitle('');
                setTags([]);
                setAim('');
                // Default date/time - Use LOCAL date
                setDate(getLocalDate());
                setHours('');
                setMinutes('');
                setError('');
                setType(defaultType);
            }
        }
    }, [isOpen, initialData, defaultType]);

    const handleAddTag = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && tagInput.trim()) {
            e.preventDefault();
            if (!tags.includes(tagInput.trim())) {
                setTags([...tags, tagInput.trim()]);
            }
            setTagInput('');
        }
    };

    const removeTag = (tagToRemove: string) => {
        setTags(tags.filter(tag => tag !== tagToRemove));
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();

        // Validate duration
        if (!hours && !minutes) {
            setError('Please enter a duration');
            return;
        }
        setError('');


        const h = parseInt(hours || '0', 10);
        const m = parseInt(minutes || '0', 10);

        let durStr = '';
        if (h > 0) durStr += `${h}h`;
        if (m > 0) durStr += ` ${m}m`;
        durStr = durStr.trim();

        if (!durStr) durStr = '0m';

        const localToday = getLocalDate();
        const taskData = {
            title,
            tags,
            aim,
            date,
            duration: durStr,
            type: (type === 'done' ? 'done' : (date === localToday ? 'today' : 'upcoming')) as TaskType,
            isCompleted: type === 'done',
        };
        onSave(taskData);
        onClose();
    };

    // Lock date if it's a "Today" task (or intended to be)
    const isDateLocked = type === 'today';

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
                                    {initialData ? 'Edit Task' : 'Add New Task'}
                                </h2>
                                <button onClick={onClose} className="text-gray-400 hover:text-gray-600 transition-colors">
                                    <FiX size={20} />
                                </button>
                            </div>

                            <form onSubmit={handleSubmit} className="space-y-4">
                                {/* Title */}
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Task Title</label>
                                    <input
                                        type="text"
                                        value={title}
                                        onChange={(e) => setTitle(e.target.value)}
                                        className="w-full px-4 py-2 rounded-xl border border-gray-200 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 outline-none transition-all text-gray-900"
                                        placeholder="What needs to be done?"
                                        required
                                    />
                                </div>

                                {/* Tags */}
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Tags</label>
                                    <div className="flex flex-wrap gap-2 mb-2">
                                        {tags.map(tag => (
                                            <span key={tag} className="inline-flex items-center gap-1 px-2 py-1 rounded-lg bg-gray-100 text-gray-600 text-xs font-medium">
                                                {tag}
                                                <button type="button" onClick={() => removeTag(tag)} className="hover:text-red-500">
                                                    <FiX size={12} />
                                                </button>
                                            </span>
                                        ))}
                                    </div>
                                    <div className="relative">
                                        <FiTag className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={16} />
                                        <input
                                            type="text"
                                            value={tagInput}
                                            onChange={(e) => setTagInput(e.target.value)}
                                            onKeyDown={handleAddTag}
                                            className="w-full pl-10 pr-4 py-2 rounded-xl border border-gray-200 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 outline-none transition-all"
                                            placeholder="Add tag and press Enter"
                                        />
                                    </div>
                                </div>

                                {/* Aim */}
                                <div>
                                    <label className="block text-sm font-medium text-black mb-1">Aim / Description</label>
                                    <textarea
                                        value={aim}
                                        onChange={(e) => setAim(e.target.value)}
                                        rows={3}
                                        className="w-full px-4 py-2 rounded-xl border border-gray-200 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 outline-none transition-all resize-none text-black"
                                        placeholder="Describe the goal of this task..."
                                    />
                                </div>

                                {/* Date & Time */}
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">Date</label>
                                        <div className="relative">
                                            <FiCalendar className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={16} />
                                            <input
                                                type="date"
                                                value={date}
                                                onChange={(e) => setDate(e.target.value)}
                                                disabled={isDateLocked && !initialData} // Lock only if creating new Today task, allow edit if needed or logic dictates
                                                // Actually requirement says: "For Today box -> date picker locked to today"
                                                // So if type === 'today', we should lock it or force it to today.
                                                readOnly={type === 'today'}
                                                className={clsx(
                                                    "w-full pl-10 pr-4 py-2 rounded-xl border border-gray-200 outline-none transition-all",
                                                    type === 'today'
                                                        ? "bg-gray-50 text-gray-500 cursor-not-allowed"
                                                        : "focus:border-primary-500 focus:ring-2 focus:ring-primary-200 text-gray-900"
                                                )}
                                            />
                                        </div>
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">Duration</label>
                                        <div className="flex gap-2">
                                            <div className="relative flex-1">
                                                <input
                                                    type="number"
                                                    min="0"
                                                    value={hours}
                                                    onChange={(e) => setHours(e.target.value)}
                                                    className="w-full px-3 py-2 rounded-xl border border-gray-200 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 outline-none transition-all text-gray-900"
                                                    placeholder="Hrs"
                                                />
                                            </div>
                                            <div className="relative flex-1">
                                                <input
                                                    type="number"
                                                    min="0"
                                                    max="59"
                                                    value={minutes}
                                                    onChange={(e) => setMinutes(e.target.value)}
                                                    className="w-full px-3 py-2 rounded-xl border border-gray-200 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 outline-none transition-all text-gray-900"
                                                    placeholder="Min"
                                                />
                                            </div>
                                        </div>
                                        {error && <p className="text-red-500 text-xs mt-1 ml-1">{error}</p>}
                                    </div>
                                </div>

                                {/* Actions */}
                                <div className="flex items-center justify-end gap-3 pt-4 border-t border-gray-50">
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
                            </form>
                        </div>
                    </motion.div >
                </>
            )
            }
        </AnimatePresence >
    );
}
