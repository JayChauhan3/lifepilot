"use client";

import { useEffect, useMemo } from "react";
import { motion } from "framer-motion";
import { FiClock, FiBriefcase, FiCoffee, FiShoppingBag, FiMoon, FiActivity, FiAlertCircle, FiCheckCircle, FiSun, FiBook, FiArrowRight } from "react-icons/fi";
import Link from "next/link";
import clsx from "clsx";
import { usePlannerStore } from "../../store/plannerStore";
import { Task, Routine } from "../../types/planner";

// Helper to map icon string to component
const ICON_MAP: Record<string, any> = {
    FiSun, FiMoon, FiBriefcase, FiActivity, FiBook, FiCoffee, FiShoppingBag
};

// Static style map for timeline items
const TIMELINE_STYLES: Record<string, { dotBorder: string, dotText: string, dotBgHover: string, dotBorderHover: string, dotFill: string, labelBg: string, labelText: string }> = {
    routine: {
        dotBorder: "border-amber-100",
        dotText: "text-amber-500",
        dotBgHover: "group-hover:bg-amber-50",
        dotBorderHover: "group-hover:border-amber-500",
        dotFill: "bg-amber-500",
        labelBg: "bg-amber-100",
        labelText: "text-amber-700"
    },
    work: {
        dotBorder: "border-blue-100",
        dotText: "text-blue-500",
        dotBgHover: "group-hover:bg-blue-50",
        dotBorderHover: "group-hover:border-blue-500",
        dotFill: "bg-blue-500",
        labelBg: "bg-blue-100",
        labelText: "text-blue-700"
    },
    health: {
        dotBorder: "border-emerald-100",
        dotText: "text-emerald-500",
        dotBgHover: "group-hover:bg-emerald-50",
        dotBorderHover: "group-hover:border-emerald-500",
        dotFill: "bg-emerald-500",
        labelBg: "bg-emerald-100",
        labelText: "text-emerald-700"
    },
    personal: {
        dotBorder: "border-rose-100",
        dotText: "text-rose-500",
        dotBgHover: "group-hover:bg-rose-50",
        dotBorderHover: "group-hover:border-rose-500",
        dotFill: "bg-rose-500",
        labelBg: "bg-rose-100",
        labelText: "text-rose-700"
    },
    default: {
        dotBorder: "border-gray-100",
        dotText: "text-gray-500",
        dotBgHover: "group-hover:bg-gray-50",
        dotBorderHover: "group-hover:border-gray-500",
        dotFill: "bg-gray-500",
        labelBg: "bg-gray-100",
        labelText: "text-gray-700"
    }
};

interface TimelineItem {
    id: string;
    time: string;
    endTime?: string;
    title: string;
    type: string;
    icon?: any;
    isWorkBlock?: boolean;
    subTasks?: Task[];
    isOverloaded?: boolean;
}

export default function TodayPlan() {
    const { tasks, routines, fetchTasks, fetchRoutines } = usePlannerStore();

    useEffect(() => {
        fetchTasks();
        fetchRoutines();
    }, [fetchTasks, fetchRoutines]);

    const timelineItems = useMemo(() => {
        const todayTasks = tasks.filter(t => t.type === 'today' && !t.isCompleted);
        const workRoutine = routines.find(r => r.isWorkBlock || r.title.toLowerCase().includes('work'));

        // 1. Identify Work Tasks (no time set, or explicitly tagged 'Work')
        // For simplicity, we'll assume tasks without a specific time (or default 00:00/empty) go to work block
        // Or if we want to be stricter: tasks that don't have a time set.
        // But our Task model has 'time'. Let's assume if time is "09:00" (start of work) or just generic, it goes to work.
        // User requirement: "tasks only goes in work hours which is in routine"
        // So we'll put ALL today tasks into the work block UNLESS they have a specific time that is OUTSIDE work hours?
        // Simpler approach: Put all tasks into work block, unless they are clearly "Personal" or have a time that conflicts with another routine?
        // Let's stick to the plan: "Tasks without a specific time set" -> Work Block.
        // But wait, the TaskModal forces a time.
        // Let's assume tasks scheduled strictly within the Work Routine's start/end time are "Work Tasks".

        let workStartTime = "09:00";
        let workDurationMins = 8 * 60; // Default 8h

        if (workRoutine) {
            workStartTime = workRoutine.startTime || "09:00";
            // Parse duration (e.g., "8h", "45m")
            const dur = (workRoutine.duration || "8h").toLowerCase();
            if (dur.includes('h')) workDurationMins = parseFloat(dur) * 60;
            else if (dur.includes('m')) workDurationMins = parseFloat(dur);
        }

        const [workStartHour, workStartMin] = workStartTime.split(':').map(Number);
        const workStartTotalMins = workStartHour * 60 + workStartMin;
        const workEndTotalMins = workStartTotalMins + workDurationMins;

        const workBlockTasks: Task[] = [];
        const otherItems: TimelineItem[] = [];

        // Process Routines
        routines.forEach(routine => {
            let type = 'routine';
            const lowerTitle = routine.title.toLowerCase();
            if (routine.isWorkBlock || lowerTitle.includes('work')) type = 'work';
            else if (lowerTitle.includes('gym') || lowerTitle.includes('health')) type = 'health';

            const Icon = ICON_MAP[routine.icon || 'FiActivity'] || FiActivity;

            if (type === 'work') {
                // This is the container
                // We will add it later with subtasks
            } else {
                otherItems.push({
                    id: routine.id,
                    time: formatTime(routine.startTime),
                    endTime: formatTime(routine.endTime),
                    title: routine.title,
                    type,
                    icon: Icon
                });
            }
        });

        // Process Tasks
        todayTasks.forEach(task => {
            // User Request: "tasks only goes in work hours which is in routine"
            // Interpretation: The Work Block is the container for ALL tasks for the day.
            // We group all tasks into the Work Block regardless of their specific time, 
            // assuming the user wants to manage them within that block.
            workBlockTasks.push(task);
        });

        // Construct Work Block Item
        if (workRoutine) {
            // Calculate overload
            // Assume 30 mins per task
            const estimatedTaskDuration = workBlockTasks.length * 30;
            const isOverloaded = estimatedTaskDuration > workDurationMins;

            otherItems.push({
                id: workRoutine.id,
                time: formatTime(workRoutine.startTime),
                endTime: formatTime(workRoutine.endTime),
                title: workRoutine.title,
                type: 'work',
                icon: FiBriefcase,
                isWorkBlock: true,
                subTasks: workBlockTasks,
                isOverloaded
            });
        }

        // Sort by time
        return otherItems.sort((a, b) => {
            const timeA = parseTime(a.time);
            const timeB = parseTime(b.time);
            return timeA - timeB;
        });

    }, [tasks, routines]);

    return (
        <div className="bg-white rounded-2xl p-6 shadow-soft border border-gray-100 h-full overflow-y-auto custom-scrollbar">
            <div className="flex items-center justify-between mb-6">
                <h2 className="text-lg font-bold text-gray-900">Today's Plan</h2>
                <Link href="/tasks" className="text-primary-600 hover:text-primary-700 transition-colors p-1 hover:bg-primary-50 rounded-full">
                    <FiArrowRight size={20} />
                </Link>
            </div>

            <div className="relative">
                {/* Vertical Line */}
                <div className="absolute left-3.5 top-2 bottom-4 w-0.5 bg-gray-100" />

                <div className="space-y-6">
                    {timelineItems.map((item, index) => {
                        const styles = TIMELINE_STYLES[item.type] || TIMELINE_STYLES.default;

                        return (
                            <motion.div
                                key={item.id}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.1 + index * 0.05 }}
                                className="relative flex gap-4 group"
                            >
                                {/* Dot/Icon */}
                                <div className={clsx(
                                    "relative z-10 w-7 h-7 rounded-full flex items-center justify-center border-2 bg-white transition-colors duration-300 shrink-0",
                                    styles.dotBorder,
                                    styles.dotText,
                                    styles.dotBorderHover,
                                    styles.dotBgHover
                                )}>
                                    {item.icon ? <item.icon size={14} /> : <div className={clsx("w-2 h-2 rounded-full", styles.dotFill)} />}
                                </div>

                                {/* Content */}
                                <div className="flex-1 pb-1">
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <h3 className="text-sm font-medium text-gray-900 group-hover:text-primary-600 transition-colors">
                                                {item.title}
                                            </h3>
                                            <div className="flex items-center gap-1.5 mt-0.5">
                                                <FiClock className="text-gray-400" size={12} />
                                                <span className="text-xs text-gray-500">
                                                    {item.time}{item.endTime && ` - ${item.endTime}`}
                                                </span>
                                            </div>
                                        </div>
                                        <span className={clsx(
                                            "text-[10px] px-2 py-0.5 rounded-full font-medium uppercase tracking-wide self-start mt-0.5",
                                            styles.labelBg,
                                            styles.labelText
                                        )}>
                                            {item.type}
                                        </span>
                                    </div>

                                    {/* Work Block Subtasks */}
                                    {item.isWorkBlock && item.subTasks && item.subTasks.length > 0 && (
                                        <div key={`work-block-${item.id}`} className="mt-2 bg-blue-50/30 rounded-xl p-2 border border-blue-100/50">
                                            {item.isOverloaded && (
                                                <div key={`overload-${item.id}`} className="flex items-center gap-2 text-xs text-amber-600 bg-amber-50 px-2 py-1 rounded-lg mb-2 border border-amber-100">
                                                    <FiAlertCircle size={12} />
                                                    <span>Overload!</span>
                                                </div>
                                            )}
                                            <div className="space-y-1">
                                                {item.subTasks.map((task, taskIndex) => (
                                                    <div
                                                        key={`task-${task.id || `task-${taskIndex}`}`}
                                                        className={clsx(
                                                            "flex items-center justify-between gap-2 text-xs px-2 py-1.5 rounded-lg border transition-colors",
                                                            task.isCompleted
                                                                ? "bg-gray-50/50 text-gray-400 border-transparent"
                                                                : "bg-white text-gray-600 border-blue-100/30 shadow-sm"
                                                        )}
                                                    >
                                                        <div className="flex items-center gap-2">
                                                            {task.isCompleted ? (
                                                                <FiCheckCircle size={14} className="text-green-500" />
                                                            ) : (
                                                                <div className="w-2 h-2 rounded-full bg-blue-400" />
                                                            )}
                                                            <span className={clsx(
                                                                "line-clamp-1",
                                                                task.isCompleted && "line-through"
                                                            )}>
                                                                {task.title}
                                                            </span>
                                                        </div>
                                                        {task.time && task.time !== "00:00" && (
                                                            <span key={`time-${task.id || taskIndex}`} className="text-[10px] text-gray-400 whitespace-nowrap">
                                                                {formatTime(task.time)}
                                                            </span>
                                                        )}
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </motion.div>
                        );
                    })}

                    {timelineItems.length === 0 && (
                        <div className="text-center py-10 text-gray-400 text-sm">
                            No plan for today yet.
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

function formatTime(timeStr: string) {
    if (!timeStr) return "";

    // If already in 12h format, return as is
    if (timeStr.includes('AM') || timeStr.includes('PM')) {
        return timeStr;
    }

    const parts = timeStr.split(':');
    if (parts.length !== 2) return timeStr; // Return as-is if invalid format

    const hours = parseInt(parts[0], 10);
    const minutes = parseInt(parts[1], 10);

    // Check for NaN
    if (isNaN(hours) || isNaN(minutes)) return timeStr;

    const period = hours >= 12 ? 'PM' : 'AM';
    const hours12 = hours % 12 || 12;

    return `${hours12}:${minutes.toString().padStart(2, '0')} ${period}`;
}

function calculateEndTime(startTime: string, duration: string): string {
    if (!startTime || !duration) return startTime;

    const [startHour, startMin] = startTime.split(':').map(Number);
    const startTotalMins = startHour * 60 + startMin;

    // Parse duration (e.g., "8h", "45m", "1h 30m")
    let durationMins = 0;
    const dur = duration.toLowerCase();
    const hourMatch = dur.match(/(\d+)h/);
    const minMatch = dur.match(/(\d+)m/);

    if (hourMatch) durationMins += parseInt(hourMatch[1]) * 60;
    if (minMatch) durationMins += parseInt(minMatch[1]);

    const endTotalMins = startTotalMins + durationMins;
    const endHour = Math.floor(endTotalMins / 60) % 24;
    const endMin = endTotalMins % 60;

    return `${endHour.toString().padStart(2, '0')}:${endMin.toString().padStart(2, '0')}`;
}

function parseTime(timeStr: string) {
    // Convert "8:00 AM" back to minutes for sorting
    const [time, modifier] = timeStr.split(' ');
    let [hours, minutes] = time.split(':').map(Number);
    if (hours === 12 && modifier?.toLowerCase() === 'am') hours = 0;
    if (hours !== 12 && modifier?.toLowerCase() === 'pm') hours += 12;
    return hours * 60 + minutes;
}
