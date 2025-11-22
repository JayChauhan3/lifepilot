"use client";

import { motion } from "framer-motion";
import { FiPlus, FiMoreHorizontal, FiCalendar, FiFlag, FiCheckCircle } from "react-icons/fi";
import clsx from "clsx";

const COLUMNS = [
    { id: "today", title: "Today", count: 3 },
    { id: "upcoming", title: "Upcoming", count: 5 },
    { id: "done", title: "Done", count: 12 },
];

const TASKS = {
    today: [
        { id: 1, title: "Review Q3 Marketing Plan", tag: "Work", priority: "high", date: "Today" },
        { id: 2, title: "Call with Design Team", tag: "Meeting", priority: "medium", date: "2:00 PM" },
        { id: 3, title: "Buy Groceries", tag: "Personal", priority: "low", date: "5:30 PM" },
    ],
    upcoming: [
        { id: 4, title: "Update Website Copy", tag: "Project", priority: "medium", date: "Tomorrow" },
        { id: 5, title: "Prepare Monthly Report", tag: "Admin", priority: "high", date: "Nov 24" },
    ],
    done: [
        { id: 6, title: "Morning Standup", tag: "Meeting", priority: "low", date: "9:00 AM" },
    ]
};

export default function KanbanBoard() {
    return (
        <div className="h-full overflow-x-auto pb-4">
            <div className="flex gap-6 min-w-[800px] h-full">
                {COLUMNS.map((col) => (
                    <div key={col.id} className="flex-1 min-w-[300px] flex flex-col h-full">
                        {/* Column Header */}
                        <div className="flex items-center justify-between mb-4 px-1">
                            <div className="flex items-center gap-2">
                                <h3 className="font-bold text-gray-700">{col.title}</h3>
                                <span className="bg-gray-100 text-gray-500 text-xs font-medium px-2 py-0.5 rounded-full">
                                    {col.count}
                                </span>
                            </div>
                            <div className="flex gap-1">
                                <button className="p-1 hover:bg-gray-100 rounded text-gray-400 hover:text-gray-600">
                                    <FiPlus size={16} />
                                </button>
                                <button className="p-1 hover:bg-gray-100 rounded text-gray-400 hover:text-gray-600">
                                    <FiMoreHorizontal size={16} />
                                </button>
                            </div>
                        </div>

                        {/* Tasks List */}
                        <div className="flex-1 bg-gray-50/50 rounded-2xl p-3 space-y-3 overflow-y-auto custom-scrollbar border border-gray-100/50">
                            {TASKS[col.id as keyof typeof TASKS]?.map((task, index) => (
                                <TaskCard key={task.id} task={task} index={index} isDone={col.id === "done"} />
                            ))}

                            {col.id === "today" && (
                                <button className="w-full py-3 border-2 border-dashed border-gray-200 rounded-xl text-gray-400 text-sm font-medium hover:border-primary-300 hover:text-primary-600 hover:bg-primary-50/50 transition-all flex items-center justify-center gap-2">
                                    <FiPlus size={16} />
                                    Add Task
                                </button>
                            )}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

function TaskCard({ task, index, isDone }: { task: any, index: number, isDone?: boolean }) {
    return (
        <motion.div
            layout
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
            className={clsx(
                "bg-white p-4 rounded-xl border shadow-sm hover:shadow-md transition-all duration-200 cursor-grab active:cursor-grabbing group",
                isDone ? "border-gray-100 opacity-60" : "border-gray-100 hover:border-primary-200"
            )}
        >
            <div className="flex items-start justify-between gap-3 mb-2">
                <h4 className={clsx(
                    "text-sm font-medium leading-snug",
                    isDone ? "text-gray-500 line-through" : "text-gray-900 group-hover:text-primary-700"
                )}>
                    {task.title}
                </h4>
                {isDone ? (
                    <FiCheckCircle className="text-green-500 shrink-0 mt-0.5" size={16} />
                ) : (
                    <div className={clsx(
                        "w-2 h-2 rounded-full shrink-0 mt-1.5",
                        task.priority === "high" ? "bg-rose-500" :
                            task.priority === "medium" ? "bg-amber-500" : "bg-blue-500"
                    )} />
                )}
            </div>

            <div className="flex items-center justify-between mt-3">
                <div className="flex items-center gap-2">
                    <span className="px-2 py-1 bg-gray-50 text-gray-600 text-[10px] font-medium uppercase tracking-wide rounded-md border border-gray-100">
                        {task.tag}
                    </span>
                    {task.id === 1 && (
                        <span className="px-2 py-1 bg-amber-50 text-amber-600 text-[10px] font-medium uppercase tracking-wide rounded-md border border-amber-100 flex items-center gap-1">
                            ⚡ AI
                        </span>
                    )}
                </div>

                <div className="flex items-center gap-1 text-xs text-gray-400">
                    <FiCalendar size={12} />
                    <span>{task.date}</span>
                </div>
            </div>
        </motion.div>
    );
}
