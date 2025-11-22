"use client";

import { motion } from "framer-motion";
import { FiMoreHorizontal, FiClock, FiCheckCircle } from "react-icons/fi";
import clsx from "clsx";

const TASKS = {
    today: [
        { id: 1, title: "Review Q3 Marketing Plan", tag: "Work", color: "blue" },
        { id: 2, title: "Call with Design Team", tag: "Meeting", color: "purple" },
    ],
    upcoming: [
        { id: 3, title: "Update Website Copy", tag: "Project", color: "indigo" },
        { id: 4, title: "Prepare Monthly Report", tag: "Admin", color: "gray" },
    ],
    done: [
        { id: 5, title: "Morning Standup", tag: "Meeting", color: "purple" },
    ]
};

export default function TaskBoard() {
    return (
        <div className="bg-white rounded-2xl p-6 shadow-soft border border-gray-100 h-full">
            <div className="flex items-center justify-between mb-6">
                <h2 className="text-lg font-bold text-gray-900">Tasks</h2>
                <button className="text-gray-400 hover:text-gray-600">
                    <FiMoreHorizontal size={20} />
                </button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 h-full">
                {/* Today Column */}
                <div className="space-y-3">
                    <div className="flex items-center justify-between text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
                        <span>Today</span>
                        <span className="bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded-md">{TASKS.today.length}</span>
                    </div>
                    {TASKS.today.map((task, i) => (
                        <TaskCard key={task.id} task={task} index={i} />
                    ))}
                </div>

                {/* Upcoming Column */}
                <div className="space-y-3">
                    <div className="flex items-center justify-between text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
                        <span>Upcoming</span>
                        <span className="bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded-md">{TASKS.upcoming.length}</span>
                    </div>
                    {TASKS.upcoming.map((task, i) => (
                        <TaskCard key={task.id} task={task} index={i} delay={0.1} />
                    ))}
                </div>

                {/* Done Column */}
                <div className="space-y-3">
                    <div className="flex items-center justify-between text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
                        <span>Done</span>
                        <span className="bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded-md">{TASKS.done.length}</span>
                    </div>
                    {TASKS.done.map((task, i) => (
                        <TaskCard key={task.id} task={task} index={i} delay={0.2} isDone />
                    ))}
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
                <span className={clsx(
                    "text-[10px] px-2 py-0.5 rounded-full font-medium",
                    `bg-${task.color}-50 text-${task.color}-600`
                )}>
                    {task.tag}
                </span>
                {!isDone && (
                    <FiClock className="text-gray-300 group-hover:text-primary-400 transition-colors" size={14} />
                )}
            </div>
        </motion.div>
    );
}
