"use client";

import { motion } from "framer-motion";
import { FiMoreHorizontal, FiClock, FiCheckCircle } from "react-icons/fi";
import clsx from "clsx";

import { useEffect } from "react";
import { usePlannerStore } from "@/store/plannerStore";
import { Task } from "@/types/planner";

// Helper to get color based on tag
const getTagColor = (tag: string = ""): keyof typeof TAG_STYLES => {
    const colors = Object.keys(TAG_STYLES) as (keyof typeof TAG_STYLES)[];
    const index = tag.split("").reduce((acc, char) => acc + char.charCodeAt(0), 0);
    return colors[index % colors.length];
};

const TAG_STYLES = {
    blue: "bg-blue-50 text-blue-600",
    purple: "bg-purple-50 text-purple-600",
    indigo: "bg-indigo-50 text-indigo-600",
    pink: "bg-pink-50 text-pink-600",
    orange: "bg-orange-50 text-orange-600",
    teal: "bg-teal-50 text-teal-600",
    cyan: "bg-cyan-50 text-cyan-600",
};

export default function TaskBoard() {
    const { tasks, fetchTasks } = usePlannerStore();

    useEffect(() => {
        fetchTasks();
    }, [fetchTasks]);

    // Filter tasks - only Today and Upcoming
    const todayTasks = tasks.filter(t => t.type === 'today' && !t.isCompleted);
    const upcomingTasks = tasks.filter(t => t.type === 'upcoming' && !t.isCompleted);

    // Map to display format
    const mapTask = (task: Task) => ({
        id: task.id,
        title: task.title,
        tags: task.tags && task.tags.length > 0 ? task.tags : ["General"],
    });

    return (
        <div className="bg-white rounded-2xl p-6 shadow-soft border border-gray-100 h-full">
            <div className="flex items-center justify-between mb-6">
                <h2 className="text-lg font-bold text-gray-900">Tasks</h2>
                <button className="text-gray-400 hover:text-gray-600">
                    <FiMoreHorizontal size={20} />
                </button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 h-full">
                {/* Today Column */}
                <div className="space-y-3">
                    <div className="flex items-center justify-between text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
                        <span>Today</span>
                        <span className="bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded-md">{todayTasks.length}</span>
                    </div>
                    {todayTasks.length === 0 ? (
                        <div className="text-sm text-gray-400 italic p-2">No tasks for today</div>
                    ) : (
                        todayTasks.map((task, i) => (
                            <TaskCard key={task.id} task={mapTask(task)} index={i} />
                        ))
                    )}
                </div>

                {/* Upcoming Column */}
                <div className="space-y-3">
                    <div className="flex items-center justify-between text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
                        <span>Upcoming</span>
                        <span className="bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded-md">{upcomingTasks.length}</span>
                    </div>
                    {upcomingTasks.length === 0 ? (
                        <div className="text-sm text-gray-400 italic p-2">No upcoming tasks</div>
                    ) : (
                        upcomingTasks.map((task, i) => (
                            <TaskCard key={task.id} task={mapTask(task)} index={i} delay={0.1} />
                        ))
                    )}
                </div>
            </div>
        </div>
    );
}

function TaskCard({ task, index, delay = 0, isDone = false }: { task: any, index: number, delay?: number, isDone?: boolean }) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 + delay + index * 0.1 }}
            className={clsx(
                "p-3 rounded-xl border transition-all duration-200 group cursor-pointer",
                isDone
                    ? "bg-gray-50 border-gray-100 opacity-70"
                    : "bg-white border-gray-100 shadow-sm hover:shadow-md hover:border-primary-200"
            )}
        >
            <div className="flex items-start justify-between gap-2">
                <p className={clsx(
                    "text-sm font-medium line-clamp-2",
                    isDone ? "text-gray-500 line-through" : "text-gray-800 group-hover:text-primary-700"
                )}>
                    {task.title}
                </p>
                {isDone && <FiCheckCircle className="text-green-500 shrink-0 mt-0.5" size={14} />}
            </div>

            <div className="mt-3 flex items-center justify-between">
                <div className="flex items-center gap-1 overflow-x-auto no-scrollbar max-w-[calc(100%-24px)]">
                    {task.tags.map((tag: string) => (
                        <span
                            key={tag}
                            className={clsx(
                                "text-[10px] px-2 py-0.5 rounded-full font-medium shrink-0 whitespace-nowrap",
                                TAG_STYLES[getTagColor(tag)]
                            )}
                        >
                            {tag}
                        </span>
                    ))}
                </div>
                {!isDone && (
                    <FiClock className="text-gray-300 group-hover:text-primary-400 transition-colors shrink-0" size={14} />
                )}
            </div>
        </motion.div>
    );
}
