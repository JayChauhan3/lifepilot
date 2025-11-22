"use client";

import { useState } from "react";
import KanbanBoard from "@/components/tasks/KanbanBoard";
import RoutinesView from "@/components/routines/RoutinesView";
import { FiList, FiActivity } from "react-icons/fi";
import clsx from "clsx";

export default function TasksPage() {
    const [activeTab, setActiveTab] = useState<"tasks" | "routines">("tasks");

    return (
        <div className="flex flex-col h-[calc(100vh-8rem)]">
            {/* Header & Tabs */}
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 tracking-tight">Tasks & Routines</h1>
                    <p className="text-gray-500 text-sm">Manage your daily tasks and automated routines</p>
                </div>

                <div className="flex bg-gray-100/80 p-1 rounded-xl">
                    <button
                        onClick={() => setActiveTab("tasks")}
                        className={clsx(
                            "flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200",
                            activeTab === "tasks"
                                ? "bg-white text-primary-600 shadow-sm"
                                : "text-gray-500 hover:text-gray-700"
                        )}
                    >
                        <FiList size={16} />
                        Tasks
                    </button>
                    <button
                        onClick={() => setActiveTab("routines")}
                        className={clsx(
                            "flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200",
                            activeTab === "routines"
                                ? "bg-white text-primary-600 shadow-sm"
                                : "text-gray-500 hover:text-gray-700"
                        )}
                    >
                        <FiActivity size={16} />
                        Routines
                    </button>
                </div>
            </div>

            {/* Content Area */}
            <div className="flex-1 min-h-0">
                {activeTab === "tasks" ? (
                    <KanbanBoard />
                ) : (
                    <div className="h-full overflow-y-auto pr-2 custom-scrollbar">
                        <RoutinesView />
                    </div>
                )}
            </div>
        </div>
    );
}
