"use client";

import {
    DndContext,
    closestCenter,
    KeyboardSensor,
    PointerSensor,
    useSensor,
    useSensors,
    DragEndEvent
} from '@dnd-kit/core';
import {
    arrayMove,
    SortableContext,
    sortableKeyboardCoordinates,
    verticalListSortingStrategy,
    useSortable
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { FiPlus, FiMoreHorizontal, FiCalendar, FiTrash2, FiCheckCircle, FiSquare } from "react-icons/fi";
import clsx from "clsx";
import { usePlannerStore } from "../../store/plannerStore";
import { Task, TaskType } from "../../types/planner";
import TaskModal from "../planner/TaskModal";
import ConfirmationModal from "../planner/ConfirmationModal";

function SortableTaskCard({ task, index, onClick, onCheckboxClick, onDelete }: any) {
    const {
        attributes,
        listeners,
        setNodeRef,
        transform,
        transition,
    } = useSortable({ id: task.id });

    const style = {
        transform: CSS.Transform.toString(transform),
        transition,
    };

    return (
        <div ref={setNodeRef} style={style} {...attributes} {...listeners} className="touch-none">
            <TaskCard
                task={task}
                index={index}
                onClick={onClick}
                onCheckboxClick={onCheckboxClick}
                onDelete={onDelete}
            />
        </div>
    );
}

const COLUMNS: { id: TaskType; title: string }[] = [
    { id: "today", title: "Today" },
    { id: "upcoming", title: "Upcoming" },
    { id: "unfinished", title: "Unfinished" },
    { id: "done", title: "Done" },
];

export default function KanbanBoard() {
    const {
        tasks,
        fetchTasks,
        fetchRoutines,
        addTask,
        updateTask,
        deleteTask,
        deleteTasksByType,
        toggleTaskCompletion,
        reorderTasks,
        isLoading
    } = usePlannerStore();
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [editingTask, setEditingTask] = useState<Task | undefined>(undefined);
    const [modalDefaultType, setModalDefaultType] = useState<TaskType>('today');

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
        fetchTasks();
        fetchRoutines();
    }, [fetchTasks, fetchRoutines]);

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
        setConfirmConfig({
            isOpen: true,
            title: 'Delete All Tasks?',
            message: `Are you sure you want to delete all tasks in ${type}? This action cannot be undone.`,
            onConfirm: () => deleteTasksByType(type),
            isDanger: true,
        });
    };

    const handleDeleteTask = (task: Task) => {
        setConfirmConfig({
            isOpen: true,
            title: 'Delete Task?',
            message: `Are you sure you want to delete "${task.title}"?`,
            onConfirm: () => deleteTask(task.id),
            isDanger: true,
        });
    };

    const handleCheckboxClick = (task: Task, e: React.MouseEvent) => {
        e.stopPropagation();
        if (task.type === 'today' && !task.isCompleted) {
            setConfirmConfig({
                isOpen: true,
                title: 'Are you finished with this task?',
                message: `"${task.title}" will be moved to Done.`,
                onConfirm: () => toggleTaskCompletion(task.id),
                isDanger: false,
            });
        } else {
            toggleTaskCompletion(task.id);
        }
    };

    const sensors = useSensors(
        useSensor(PointerSensor, {
            activationConstraint: {
                distance: 8,
            },
        }),
        useSensor(KeyboardSensor, {
            coordinateGetter: sortableKeyboardCoordinates,
        })
    );

    const handleDragEnd = (event: DragEndEvent) => {
        const { active, over } = event;
        console.log('DragEnd:', active.id, 'over', over?.id);

        if (active.id !== over?.id) {
            const todayTasks = tasks
                .filter(t => t.type === 'today')
                .sort((a, b) => (a.priorityIndex ?? 0) - (b.priorityIndex ?? 0));

            const oldIndex = todayTasks.findIndex((t) => t.id === active.id);
            const newIndex = todayTasks.findIndex((t) => t.id === over?.id);

            console.log('Reordering:', oldIndex, '->', newIndex);

            if (oldIndex !== -1 && newIndex !== -1) {
                const newOrder = arrayMove(todayTasks, oldIndex, newIndex);
                const newIds = newOrder.map(t => t.id);
                console.log('New IDs order:', newIds);
                reorderTasks(newIds);
            }
        }
    };

    return (
        <div className="h-full flex flex-col">
            <div className="flex items-center justify-between mb-6">
                <h1 className="text-2xl font-bold text-gray-900">Tasks</h1>
                <div className="flex gap-2">
                    <button
                        onClick={() => handleAddTask('today')}
                        className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium rounded-xl shadow-sm shadow-primary-200 transition-all active:scale-95 flex items-center gap-2"
                    >
                        <FiPlus size={16} />
                        Add Task
                    </button>
                </div>
            </div>

            <DndContext
                sensors={sensors}
                collisionDetection={closestCenter}
                onDragEnd={handleDragEnd}
            >
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 h-full overflow-hidden">
                    {COLUMNS.map(col => {
                        const columnTasks = tasks
                            .filter(t => t.type === col.id)
                            .sort((a, b) => (a.priorityIndex ?? 0) - (b.priorityIndex ?? 0));

                        return (
                            <div key={col.id} className="flex flex-col h-full min-h-0 bg-gray-50/50 rounded-2xl border border-gray-100/50 p-1">
                                <div className="flex items-center justify-between px-4 py-3">
                                    <div className="flex items-center gap-2">
                                        <h3 className="font-semibold text-gray-700">{col.title}</h3>
                                        <span className="px-2 py-0.5 bg-gray-200 text-gray-600 text-xs font-medium rounded-full">
                                            {columnTasks.length}
                                        </span>
                                    </div>
                                    <button
                                        onClick={() => handleDeleteAll(col.id)}
                                        className="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                                        title="Clear All"
                                    >
                                        <FiTrash2 size={14} />
                                    </button>
                                </div>

                                <div className="flex-1 overflow-y-auto px-3 pb-3 custom-scrollbar">
                                    <div className="space-y-3 min-h-[100px]">
                                        <AnimatePresence mode="popLayout">
                                            {col.id === 'today' ? (
                                                <SortableContext
                                                    items={columnTasks.map(t => t.id)}
                                                    strategy={verticalListSortingStrategy}
                                                >
                                                    {columnTasks.map((task, index) => (
                                                        <SortableTaskCard
                                                            key={task.id}
                                                            task={task}
                                                            index={index}
                                                            onClick={() => handleEditTask(task)}
                                                            onCheckboxClick={(e: any) => handleCheckboxClick(task, e)}
                                                            onDelete={() => handleDeleteTask(task)}
                                                        />
                                                    ))}
                                                </SortableContext>
                                            ) : (
                                                columnTasks.map((task, index) => (
                                                    <TaskCard
                                                        key={task.id}
                                                        task={task}
                                                        index={index}
                                                        onClick={() => handleEditTask(task)}
                                                        onCheckboxClick={(e: any) => handleCheckboxClick(task, e)}
                                                        onDelete={() => handleDeleteTask(task)}
                                                    />
                                                ))
                                            )}
                                        </AnimatePresence>

                                        {col.id !== "done" && col.id !== "unfinished" && (
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
                            </div>
                        );
                    })}
                </div>
            </DndContext>

            <TaskModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                onSave={handleSaveTask}
                initialData={editingTask}
                defaultType={modalDefaultType}
            />

            <ConfirmationModal
                isOpen={confirmConfig.isOpen}
                onClose={() => setConfirmConfig(prev => ({ ...prev, isOpen: false }))}
                onConfirm={confirmConfig.onConfirm}
                title={confirmConfig.title}
                message={confirmConfig.message}
                isDanger={confirmConfig.isDanger}
                confirmText={confirmConfig.isDanger ? 'Delete' : 'Yes'}
            />
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
                            onClick={(e) => {
                                e.stopPropagation();
                                onCheckboxClick(e);
                            }}
                            className={clsx(
                                "mt-0.5 shrink-0 transition-colors relative z-10",
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

                {/* Delete Icon */}
                <button
                    onClick={onDelete}
                    className="text-gray-300 hover:text-red-500 transition-colors p-1 -mr-1 opacity-0 group-hover:opacity-100"
                    title="Delete Task"
                >
                    <FiTrash2 size={14} />
                </button>
            </div>

            <div className={clsx(
                "flex items-center justify-between mt-3",
                (task.type === 'today' || isDone) ? "pl-7" : "pl-0"
            )}>
                <div className="flex items-center gap-2 overflow-x-auto no-scrollbar pb-1 -mb-1 max-w-[calc(100%-60px)]">
                    {task.tags.map(tag => (
                        <span key={tag} className="px-2 py-1 bg-gray-50 text-gray-600 text-[10px] font-medium uppercase tracking-wide rounded-md border border-gray-100 shrink-0 whitespace-nowrap">
                            {tag}
                        </span>
                    ))}
                </div>

                <div className="flex items-center gap-1 text-xs text-gray-400 shrink-0 ml-2">
                    <FiCalendar size={12} />
                    <span>{task.duration}</span>
                </div>
            </div>
        </motion.div>
    );
}
