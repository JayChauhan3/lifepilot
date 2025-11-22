"use client";

import { motion } from "framer-motion";
import { FiPlay, FiEdit2, FiClock, FiRepeat, FiSun, FiMoon, FiBriefcase, FiActivity, FiBook, FiPlus } from "react-icons/fi";
import clsx from "clsx";

const ROUTINES = [
    { id: 1, title: "Morning Routine", time: "8:00 AM", duration: "45m", icon: FiSun, type: "morning", nextRun: "Tomorrow, 8:00 AM" },
    { id: 2, title: "Deep Work Block", time: "9:00 AM", duration: "2h", icon: FiBriefcase, type: "work", nextRun: "Tomorrow, 9:00 AM" },
    { id: 3, title: "Gym Workout", time: "5:30 PM", duration: "1h", icon: FiActivity, type: "health", nextRun: "Today, 5:30 PM" },
    { id: 4, title: "Evening Wind Down", time: "9:30 PM", duration: "30m", icon: FiMoon, type: "evening", nextRun: "Today, 9:30 PM" },
    { id: 5, title: "Reading Time", time: "10:00 PM", duration: "30m", icon: FiBook, type: "leisure", nextRun: "Today, 10:00 PM" },
];

// Static style map for routines
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
    }
};

export default function RoutinesView() {
    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {ROUTINES.map((routine, index) => (
                <RoutineCard key={routine.id} routine={routine} index={index} />
            ))}

            {/* Add New Routine Card */}
            <motion.button
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.3 }}
                className="flex flex-col items-center justify-center h-full min-h-[200px] rounded-2xl border-2 border-dashed border-gray-200 bg-gray-50/50 text-gray-400 hover:border-primary-300 hover:text-primary-600 hover:bg-primary-50/30 transition-all group"
            >
                <div className="w-12 h-12 rounded-full bg-white border border-gray-200 flex items-center justify-center mb-3 group-hover:scale-110 transition-transform shadow-sm">
                    <FiPlus size={24} />
                </div>
                <span className="font-medium">Create New Routine</span>
            </motion.button>
        </div>
    );
}

function RoutineCard({ routine, index }: { routine: any, index: number }) {
    const Icon = routine.icon;
    const styles = ROUTINE_STYLES[routine.type] || ROUTINE_STYLES.morning;

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
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
                        <button className="p-2 rounded-lg hover:bg-gray-100 text-gray-400 hover:text-gray-600 transition-colors">
                            <FiEdit2 size={16} />
                        </button>
                    </div>
                </div>

                <h3 className="text-lg font-bold text-gray-900 mb-1">{routine.title}</h3>

                <div className="flex items-center gap-4 text-sm text-gray-500 mb-6">
                    <div className="flex items-center gap-1.5">
                        <FiClock size={14} />
                        <span>{routine.time}</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                        <FiRepeat size={14} />
                        <span>{routine.duration}</span>
                    </div>
                </div>

                <div className="flex items-center justify-between pt-4 border-t border-gray-50">
                    <div className="text-xs font-medium text-gray-400">
                        Next: <span className="text-gray-600">{routine.nextRun}</span>
                    </div>
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
