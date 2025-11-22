"use client";

import { motion, AnimatePresence } from "framer-motion";
import { FiActivity, FiCheck, FiLoader, FiDatabase, FiCalendar, FiSun, FiList } from "react-icons/fi";
import clsx from "clsx";
import { useEffect, useState } from "react";

type AgentAction = {
    id: string;
    agent: "Planner" | "Knowledge" | "Routine" | "Memory" | "Task Executor";
    status: "processing" | "completed" | "waiting";
    message: string;
    timestamp: Date;
};

// Static style map to ensure Tailwind classes are generated
const AGENT_STYLES = {
    "Planner": {
        icon: FiCalendar,
        bubble: "bg-blue-50 border-blue-200 text-blue-600",
        text: "text-blue-700"
    },
    "Knowledge": {
        icon: FiSun,
        bubble: "bg-amber-50 border-amber-200 text-amber-600",
        text: "text-amber-700"
    },
    "Routine": {
        icon: FiActivity,
        bubble: "bg-purple-50 border-purple-200 text-purple-600",
        text: "text-purple-700"
    },
    "Memory": {
        icon: FiDatabase,
        bubble: "bg-rose-50 border-rose-200 text-rose-600",
        text: "text-rose-700"
    },
    "Task Executor": {
        icon: FiList,
        bubble: "bg-emerald-50 border-emerald-200 text-emerald-600",
        text: "text-emerald-700"
    }
};

export default function AgentActionsPanel() {
    // Mock data simulation
    const [actions, setActions] = useState<AgentAction[]>([
        {
            id: "1",
            agent: "Planner",
            status: "completed",
            message: "Analyzed daily goals",
            timestamp: new Date(Date.now() - 10000),
        },
        {
            id: "2",
            agent: "Knowledge",
            status: "completed",
            message: "Fetched weather data: 24°C Sunny",
            timestamp: new Date(Date.now() - 5000),
        },
        {
            id: "3",
            agent: "Task Executor",
            status: "processing",
            message: "Syncing tasks to calendar...",
            timestamp: new Date(),
        },
    ]);

    return (
        <div className="bg-white rounded-2xl p-6 shadow-soft border border-gray-100 h-full overflow-hidden flex flex-col">
            <div className="flex items-center justify-between mb-6">
                <h2 className="text-lg font-bold text-gray-900">Agent Activity</h2>
                <div className="flex items-center gap-2">
                    <span className="relative flex h-2.5 w-2.5">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
                    </span>
                    <span className="text-xs font-medium text-gray-500">Live</span>
                </div>
            </div>

            <div className="space-y-4 overflow-y-auto flex-1 pr-2 custom-scrollbar">
                <AnimatePresence initial={false}>
                    {actions.map((action) => {
                        const styles = AGENT_STYLES[action.agent] || AGENT_STYLES["Routine"];
                        const Icon = styles.icon;

                        return (
                            <motion.div
                                key={action.id}
                                initial={{ opacity: 0, x: 20 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: -20 }}
                                className="relative pl-8 pb-4 last:pb-0"
                            >
                                {/* Timeline Line */}
                                <div className="absolute left-3.5 top-8 bottom-0 w-0.5 bg-gray-100 last:hidden" />

                                {/* Icon Bubble */}
                                <div className={clsx(
                                    "absolute left-0 top-0 w-7 h-7 rounded-full flex items-center justify-center border-2 z-10",
                                    styles.bubble
                                )}>
                                    <Icon size={14} />
                                </div>

                                <div className="bg-gray-50 rounded-xl p-3 border border-gray-100 hover:bg-white hover:shadow-sm transition-all duration-200">
                                    <div className="flex items-center justify-between mb-1">
                                        <span className={clsx(
                                            "text-xs font-bold uppercase tracking-wider",
                                            styles.text
                                        )}>
                                            {action.agent} Agent
                                        </span>
                                        {action.status === "processing" ? (
                                            <FiLoader className="animate-spin text-primary-500" size={14} />
                                        ) : (
                                            <FiCheck className="text-green-500" size={14} />
                                        )}
                                    </div>
                                    <p className="text-sm text-gray-700 font-medium">{action.message}</p>
                                    <p className="text-[10px] text-gray-500 mt-1">
                                        {action.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                                    </p>
                                </div>
                            </motion.div>
                        );
                    })}
                </AnimatePresence>
            </div>
        </div>
    );
}
