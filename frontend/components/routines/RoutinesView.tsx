"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { FiPlay, FiEdit2, FiClock, FiRepeat, FiSun, FiMoon, FiBriefcase, FiActivity, FiBook, FiPlus, FiTrash2, FiCoffee, FiShoppingBag } from "react-icons/fi";
import clsx from "clsx";
import { usePlannerStore } from "../../store/plannerStore";
import { Routine } from "../../types/planner";
import RoutineModal from "../planner/RoutineModal";
import ConfirmationModal from "../planner/ConfirmationModal";

// Convert 24h time string to 12h format (e.g., '13:30' -> '1:30 PM')
const to12Hour = (time24: string): string => {
    if (!time24) return '';

    // If already in 12h format, return as is
    if (time24.includes('AM') || time24.includes('PM')) {
        return time24;
    }

    const [hours, minutes] = time24.split(':').map(Number);
    const period = hours >= 12 ? 'PM' : 'AM';
    const hours12 = hours % 12 || 12;

    return `${hours12}:${minutes.toString().padStart(2, '0')} ${period}`;
};

// Helper to map icon string to component
const ICON_MAP: Record<string, any> = {
    FiSun, FiMoon, FiBriefcase, FiActivity, FiBook
};

// Static style map for routines (can be dynamic later)
const ROUTINE_STYLES: Record<string, { iconBg: string, iconColor: string, buttonBg: string, buttonText: string, gradient: string }> = {
    morning: {
        iconBg: "bg-amber-100",
        iconColor: "text-amber-600",
        buttonBg: "bg-amber-100",
        buttonText: "text-amber-700",
        gradient: "bg-amber-500"
    },
    work: {
        iconBg: "bg-blue-100",
        iconColor: "text-blue-600",
        buttonBg: "bg-blue-100",
        buttonText: "text-blue-700",
        gradient: "bg-blue-500"
    },
    health: {
        iconBg: "bg-emerald-100",
        iconColor: "text-emerald-600",
        buttonBg: "bg-emerald-100",
        buttonText: "text-emerald-700",
        gradient: "bg-emerald-500"
    },
    evening: {
        iconBg: "bg-indigo-100",
        iconColor: "text-indigo-600",
        buttonBg: "bg-indigo-100",
        buttonText: "text-indigo-700",
        gradient: "bg-indigo-500"
    },
    leisure: {
        iconBg: "bg-rose-100",
        iconColor: "text-rose-600",
        buttonBg: "bg-rose-100",
        buttonText: "text-rose-700",
        gradient: "bg-rose-500"
    },
    default: {
        iconBg: "bg-gray-100",
        iconColor: "text-gray-600",
        buttonBg: "bg-gray-100",
        buttonText: "text-gray-700",
        gradient: "bg-gray-500"
    }
};

export default function RoutinesView() {
    const { routines, fetchRoutines, addRoutine, updateRoutine, deleteRoutine } = usePlannerStore();
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [editingRoutine, setEditingRoutine] = useState<Routine | undefined>(undefined);

    // Confirmation State
    const [confirmConfig, setConfirmConfig] = useState<{
        isOpen: boolean;
        title: string;
        message: string;
        onConfirm: () => void;
        isDanger?: boolean;
    }>({
        isOpen: false,
        title: '',
        message: '',
        onConfirm: () => { },
    });

    useEffect(() => {
        fetchRoutines();
    }, [fetchRoutines]);

    const handleAddRoutine = () => {
        setEditingRoutine(undefined);
        setIsModalOpen(true);
    };

    const handleEditRoutine = (routine: Routine) => {
        setEditingRoutine(routine);
        setIsModalOpen(true);
    };

    const handleSaveRoutine = async (routineData: any) => {
        if (editingRoutine) {
            await updateRoutine(editingRoutine.id, routineData);
        } else {
            await addRoutine(routineData);
        }
    };

    const handleDeleteRoutine = async (id: string): Promise<void> => {
        // Create a promise that resolves when the user confirms the deletion
        return new Promise((resolve) => {
            setConfirmConfig({
                isOpen: true,
                title: 'Delete Routine?',
                message: 'Are you sure you want to delete this routine? This action cannot be undone.',
                onConfirm: async () => {
                    await deleteRoutine(id);
                    resolve();
                },
                isDanger: true,
            });
        });
    };

    // Helper function to convert time string to minutes for sorting
    const timeToMinutes = (timeStr: string | undefined): number => {
        if (!timeStr) return 0; // Default to midnight if no time

        // Handle 12-hour format with AM/PM
        if (timeStr.includes('AM') || timeStr.includes('PM')) {
            const [time, period] = timeStr.split(' ');
            let [hours, minutes] = time.split(':').map(Number);

            if (period === 'PM' && hours !== 12) {
                hours += 12;
            } else if (period === 'AM' && hours === 12) {
                hours = 0;
            }

            return hours * 60 + (minutes || 0);
        }

        // Handle 24-hour format
        const [hours, minutes] = timeStr.split(':').map(Number);
        return hours * 60 + (minutes || 0);
    };

    // Sort routines by start time (morning first, sleep last)
    const sortedRoutines = [...routines].sort((a, b) => {
        const aTime = timeToMinutes(a.startTime);
        const bTime = timeToMinutes(b.startTime);
        return aTime - bTime;
    });

    // Add layoutId for smooth animations when reordering
    // Include index in the layout ID to ensure uniqueness during reordering
    const getRoutineLayoutId = (id: string, index: number) => `routine-${id}-${index}`;

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Add New Routine Card - FIRST */}
            <motion.button
                layout
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0 }}
                onClick={handleAddRoutine}
                className="flex flex-col items-center justify-center h-full min-h-[200px] rounded-2xl border-2 border-dashed border-gray-200 bg-gray-50/50 text-gray-400 hover:border-primary-300 hover:text-primary-600 hover:bg-primary-50/30 transition-all group"
            >
                <div className="w-12 h-12 rounded-full bg-white border border-gray-200 flex items-center justify-center mb-3 group-hover:scale-110 transition-transform shadow-sm">
                    <FiPlus size={24} />
                </div>
                <span className="font-medium">Create New Routine</span>
            </motion.button>

            {/* Routine Cards - Sorted from Morning to Night */}
            <AnimatePresence mode="popLayout">
                {sortedRoutines.map((routine, index) => {
                    const layoutId = getRoutineLayoutId(routine.id, index);
                    return (
                        <motion.div
                            key={layoutId}
                            layoutId={layoutId}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, scale: 0.95 }}
                            transition={{ type: 'spring', stiffness: 500, damping: 50 }}
                            className="h-full"
                        >
                            <RoutineCard
                                routine={routine}
                                index={index + 1}
                                onEdit={() => handleEditRoutine(routine)}
                                onDelete={() => handleDeleteRoutine(routine.id)}
                            />
                        </motion.div>
                    )
                })}
            </AnimatePresence>

            <RoutineModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                onSave={handleSaveRoutine}
                onDelete={handleDeleteRoutine}
                initialData={editingRoutine}
            />

            <ConfirmationModal
                isOpen={confirmConfig.isOpen}
                onClose={() => setConfirmConfig(prev => ({ ...prev, isOpen: false }))}
                onConfirm={confirmConfig.onConfirm}
                title={confirmConfig.title}
                message={confirmConfig.message}
                isDanger={confirmConfig.isDanger}
                confirmText="Delete"
            />
        </div>
    );
}

function RoutineCard({ routine, index, onEdit, onDelete }: { routine: Routine, index: number, onEdit: () => void, onDelete: (id: string) => void }) {
    // Default times based on routine title
    const Icon = ICON_MAP[routine.icon || 'FiActivity'] || FiActivity;

    // Determine style based on title keywords or default
    let styleKey = 'default';
    const lowerTitle = routine.title.toLowerCase();
    if (lowerTitle.includes('morning')) styleKey = 'morning';
    else if (lowerTitle.includes('work') || lowerTitle.includes('deep')) styleKey = 'work';
    else if (lowerTitle.includes('gym') || lowerTitle.includes('health') || lowerTitle.includes('workout')) styleKey = 'health';
    else if (lowerTitle.includes('evening') || lowerTitle.includes('night')) styleKey = 'evening';
    else if (lowerTitle.includes('read') || lowerTitle.includes('book')) styleKey = 'leisure';

    const styles = ROUTINE_STYLES[styleKey];

    return (
        <motion.div
            layout
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ delay: index * 0.1 }}
            className="bg-white rounded-2xl p-6 shadow-soft border border-gray-100 hover:shadow-medium transition-all duration-300 group relative overflow-hidden"
        >
            {/* Background Gradient Decoration */}
            <div className={clsx(
                "absolute top-0 right-0 w-32 h-32 rounded-full blur-3xl -translate-y-1/2 translate-x-1/3 opacity-20 group-hover:opacity-30 transition-opacity",
                styles.gradient
            )} />

            <div className="relative z-10">
                <div className="flex items-start justify-between mb-6">
                    <div className={clsx(
                        "w-12 h-12 rounded-xl flex items-center justify-center shadow-sm transition-transform group-hover:scale-105",
                        styles.iconBg,
                        styles.iconColor
                    )}>
                        <Icon size={24} />
                    </div>
                    <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity transform translate-x-2 group-hover:translate-x-0">
                        {/* Edit Button - Always visible */}
                        <button
                            onClick={onEdit}
                            className="p-2 rounded-lg hover:bg-gray-100 text-gray-400 hover:text-gray-600 transition-colors"
                        >
                            <FiEdit2 size={16} />
                        </button>

                        {/* Delete Button - Hide for Work Block */}
                        {!routine.isWorkBlock && (
                            <button
                                onClick={() => onDelete(routine.id)}
                                className="p-2 rounded-lg hover:bg-red-50 text-gray-400 hover:text-red-500 transition-colors"
                            >
                                <FiTrash2 size={16} />
                            </button>
                        )}
                    </div>
                </div>

                <h3 className="text-lg font-bold text-gray-900 mb-1">{routine.title}</h3>

                <div className="flex items-center gap-4 text-sm text-gray-500 mb-6">
                    <div className="flex items-center gap-1.5">
                        <FiClock size={14} />
                        <span>
                            {routine.startTime ? to12Hour(routine.startTime) : '--:--'} - 
                            {routine.endTime ? to12Hour(routine.endTime) : '--:--'}
                        </span>
                    </div>
                    <div className="flex items-center gap-1.5">
                        <FiRepeat size={14} />
                        <span>{routine.duration || '--'}</span>
                    </div>
                </div>

                <div className="flex justify-end pt-4 border-t border-gray-50">
                    <button className={clsx(
                        "flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all shadow-sm hover:shadow-md active:scale-95",
                        styles.buttonBg,
                        styles.buttonText,
                        "hover:brightness-95"
                    )}>
                        <FiPlay size={14} className="fill-current" />
                        Run Now
                    </button>
                </div>
            </div>
        </motion.div>
    );
}
