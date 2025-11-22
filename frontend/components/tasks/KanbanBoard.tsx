"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { FiPlus, FiMoreHorizontal, FiCalendar, FiTrash2, FiCheckCircle, FiSquare } from "react-icons/fi";
import clsx from "clsx";
import { usePlannerStore } from "../../store/plannerStore";
import { Task, TaskType } from "../../types/planner";
import TaskModal from "../planner/TaskModal";

const COLUMNS: { id: TaskType; title: string }[] = [
    { id: "today", title: "Today" },
    { id: "upcoming", title: "Upcoming" },
    { id: "done", title: "Done" },
];

export default function KanbanBoard() {
    const { tasks, fetchTasks, addTask, updateTask, deleteTask, deleteTasksByType, toggleTaskCompletion } = usePlannerStore();
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [editingTask, setEditingTask] = useState<Task | undefined>(undefined);
    const [modalDefaultType, setModalDefaultType] = useState<TaskType>('today');

    // Confirmation Popup State
    const [confirmTask, setConfirmTask] = useState<Task | null>(null);

    useEffect(() => {
        fetchTasks();
    }, [fetchTasks]);

    const handleAddTask = (type: TaskType) => {
        setEditingTask(undefined);
        setModalDefaultType(type);
        setIsModalOpen(true);
    };

    const handleEditTask = (task: Task) => {
        setEditingTask(task);
        setIsModalOpen(true);
    };

    const handleSaveTask = async (taskData: any) => {
        if (editingTask) {
            await updateTask(editingTask.id, taskData);
        } else {
            await addTask(taskData);
        }
    };

    const handleDeleteAll = (type: TaskType) => {
        if (window.confirm(`Are you sure you want to delete all tasks in ${type}?`)) {
            deleteTasksByType(type);
        }
    };

    const handleCheckboxClick = (task: Task, e: React.MouseEvent) => {
        e.stopPropagation();
        if (task.type === 'today' && !task.isCompleted) {
            setConfirmTask(task);
        } else {
            // For other types or if already done, just toggle (or maybe disable for done?)
            // Requirement says: "Today -> Done ... Only after checkbox confirmation"
            // For Done -> Today (uncheck), requirement doesn't specify, but usually allowed.
            // Let's allow unchecking without popup.
            toggleTaskCompletion(task.id);
        }
    };

    const confirmCompletion = async () => {
        if (confirmTask) {
            await toggleTaskCompletion(confirmTask.id);
            setConfirmTask(null);
        }
    };

    return (
        <div className="h-full overflow-x-auto pb-4">
            <div className="flex gap-6 min-w-[800px] h-full">
                {COLUMNS.map((col) => {
                    const colTasks = tasks.filter(t => t.type === col.id);
                    return (
                        <div key={col.id} className="flex-1 min-w-[300px] flex flex-col h-full">
                            {/* Column Header */}
                            <div className="flex items-center justify-between mb-4 px-1">
                                <div className="flex items-center gap-2">
                                    <h3 className="font-bold text-gray-700">{col.title}</h3>
                                    <span className="bg-gray-100 text-gray-500 text-xs font-medium px-2 py-0.5 rounded-full">
                                        {colTasks.length}
                                    </span>
                                </div>
                                <div className="relative group">
                                    <button className="p-1 hover:bg-gray-100 rounded text-gray-400 hover:text-gray-600">
                                        <FiMoreHorizontal size={16} />
                                    </button>
                                    {/* Dropdown Menu */}
                                    <div className="absolute right-0 top-full mt-1 w-40 bg-white rounded-xl shadow-lg border border-gray-100 py-1 hidden group-hover:block z-10">
                                        <button
                                            onClick={() => handleDeleteAll(col.id)}
                                            className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors flex items-center gap-2"
                                        >
                                            <FiTrash2 size={14} />
                                            Delete All
                                        </button>
                                    </div>
                                </div>
                            </div>

                            {/* Tasks List */}
                            <div className="flex-1 bg-gray-50/50 rounded-2xl p-3 space-y-3 overflow-y-auto custom-scrollbar border border-gray-100/50">
                                <AnimatePresence mode="popLayout">
                                    {colTasks.map((task, index) => (
                                        <TaskCard
                                            key={task.id}
                                            task={task}
                                            index={index}
                                            isDone={col.id === "done"}
                                            onClick={() => handleEditTask(task)}
                                            onDelete={(e) => {
                                                e.stopPropagation();
                                                deleteTask(task.id);
                                            }}
                                            onCheckboxClick={(e) => handleCheckboxClick(task, e)}
                                        />
                                    ))}
                                </AnimatePresence>

                                {col.id !== "done" && (
                                    <button
                                        onClick={() => handleAddTask(col.id)}
                                        className="w-full py-3 border-2 border-dashed border-gray-200 rounded-xl text-gray-400 text-sm font-medium hover:border-primary-300 hover:text-primary-600 hover:bg-primary-50/50 transition-all flex items-center justify-center gap-2"
                                    >
                                        <FiPlus size={16} />
                                        Add Task
                                    </button>
                                )}
                            </div>
                        </div>
                    );
                })}
            </div>

            <TaskModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                onSave={handleSaveTask}
                initialData={editingTask}
                defaultType={modalDefaultType}
            />

            {/* Confirmation Popup */}
            <AnimatePresence>
                {confirmTask && (
                    <>
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="fixed inset-0 bg-black/20 backdrop-blur-sm z-50"
                            onClick={() => setConfirmTask(null)}
                        />
                        <motion.div
                            initial={{ opacity: 0, scale: 0.9, y: 20 }}
                            animate={{ opacity: 1, scale: 1, y: 0 }}
                            exit={{ opacity: 0, scale: 0.9, y: 20 }}
                            className="fixed inset-0 m-auto w-full max-w-sm h-fit bg-white rounded-2xl shadow-xl z-50 p-6 text-center"
                        >
                            <h3 className="text-lg font-bold text-gray-900 mb-2">Are you finished with this task?</h3>
                            <p className="text-gray-500 text-sm mb-6">"{confirmTask.title}" will be moved to Done.</p>
                            <div className="flex gap-3 justify-center">
                                <button
                                    onClick={() => setConfirmTask(null)}
                                    className="px-6 py-2 rounded-xl border border-gray-200 text-gray-600 font-medium hover:bg-gray-50 transition-colors"
                                >
                                    NO
                                </button>
                                <button
                                    onClick={confirmCompletion}
                                    className="px-6 py-2 rounded-xl bg-primary-600 text-white font-medium hover:bg-primary-700 transition-colors shadow-sm shadow-primary-200"
                                >
                                    YES
                                </button>
                            </div>
                        </motion.div>
                    </>
                )}
            </AnimatePresence>
        </div>
    );
}

interface TaskCardProps {
    task: Task;
    index: number;
    isDone?: boolean;
    onClick: () => void;
    onDelete: (e: React.MouseEvent) => void;
    onCheckboxClick: (e: React.MouseEvent) => void;
}

function TaskCard({ task, index, isDone, onClick, onDelete, onCheckboxClick }: TaskCardProps) {
    return (
        <motion.div
            layout
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ delay: index * 0.05 }}
            onClick={onClick}
            className={clsx(
                "bg-white p-4 rounded-xl border shadow-sm hover:shadow-md transition-all duration-200 cursor-pointer group relative",
                isDone ? "border-gray-100 opacity-60 bg-gray-50" : "border-gray-100 hover:border-primary-200"
            )}
        >
            <div className="flex items-start justify-between gap-3 mb-2">
                <div className="flex items-start gap-3 flex-1">
                    {/* Checkbox logic: Only for Today tasks or Done tasks */}
                    {(task.type === 'today' || isDone) && (
                        <button
                            onClick={onCheckboxClick}
                            className={clsx(
                                "mt-0.5 shrink-0 transition-colors",
                                isDone ? "text-green-500" : "text-gray-300 hover:text-primary-500"
                            )}
                        >
                            {isDone ? <FiCheckCircle size={18} /> : <FiSquare size={18} />}
                        </button>
                    )}

                    <h4 className={clsx(
                        "text-sm font-medium leading-snug",
                        isDone ? "text-gray-500 line-through" : "text-gray-900 group-hover:text-primary-700"
                    )}>
                        {task.title}
                    </h4>
                </div>

                {/* Delete Icon - replaces colored dot */}
                {!isDone && (
                    <button
                        onClick={onDelete}
                        className="text-gray-300 hover:text-red-500 transition-colors p-1 -mr-1 opacity-0 group-hover:opacity-100"
                        title="Delete Task"
                    >
                        <FiTrash2 size={14} />
                    </button>
                )}
            </div>

            <div className="flex items-center justify-between mt-3 pl-7">
                <div className="flex items-center gap-2 overflow-x-auto no-scrollbar pb-1 -mb-1 max-w-[calc(100%-60px)]">
                    {task.tags.map(tag => (
                        <span key={tag} className="px-2 py-1 bg-gray-50 text-gray-600 text-[10px] font-medium uppercase tracking-wide rounded-md border border-gray-100 shrink-0 whitespace-nowrap">
                            {tag}
                        </span>
                    ))}
                </div>

                <div className="flex items-center gap-1 text-xs text-gray-400 shrink-0 ml-2">
                    <FiCalendar size={12} />
                    <span>{task.time}</span>
                </div>
            </div>
        </motion.div>
    );
}
