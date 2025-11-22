"use client";

import { motion } from "framer-motion";
import { FiClock, FiBriefcase, FiCoffee, FiShoppingBag, FiMoon, FiActivity } from "react-icons/fi";
import clsx from "clsx";

const TIMELINE_ITEMS = [
    { time: "8:00 am", title: "Morning Routine", type: "routine", icon: FiCoffee },
    { time: "9:00 am", title: "Deep Work Block", type: "work", icon: FiBriefcase },
    { time: "11:30 am", title: "Gym", type: "health", icon: FiActivity },
    { time: "2:00 pm", title: "Lunch + Shopping List", type: "personal", icon: FiShoppingBag },
    { time: "5:00 pm", title: "Project Work", type: "work", icon: FiBriefcase },
    { time: "9:00 pm", title: "Relax Wind Down", type: "routine", icon: FiMoon },
];

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
    }
};

export default function TodayPlan() {
    return (
        <div className="bg-white rounded-2xl p-6 shadow-soft border border-gray-100 h-full">
            <div className="flex items-center justify-between mb-6">
                <h2 className="text-lg font-bold text-gray-900">Today's Plan</h2>
                <button className="text-sm text-primary-600 font-medium hover:text-primary-700">
                    View Full
                </button>
            </div>

            <div className="relative">
                {/* Vertical Line */}
                <div className="absolute left-3.5 top-2 bottom-4 w-0.5 bg-gray-100" />

                <div className="space-y-6">
                    {TIMELINE_ITEMS.map((item, index) => {
                        const styles = TIMELINE_STYLES[item.type] || TIMELINE_STYLES.routine;

                        return (
                            <motion.div
                                key={index}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.3 + index * 0.1 }}
                                className="relative flex gap-4 group"
                            >
                                {/* Dot/Icon */}
                                <div className={clsx(
                                    "relative z-10 w-7 h-7 rounded-full flex items-center justify-center border-2 bg-white transition-colors duration-300",
                                    styles.dotBorder,
                                    styles.dotText,
                                    styles.dotBorderHover,
                                    styles.dotBgHover
                                )}>
                                    <div className={clsx("w-2 h-2 rounded-full", styles.dotFill)} />
                                </div>

                                {/* Content */}
                                <div className="flex-1 -mt-1 pb-1">
                                    <div className="flex items-center justify-between">
                                        <span className="text-xs font-medium text-gray-400 font-mono">
                                            {item.time}
                                        </span>
                                        <span className={clsx(
                                            "text-[10px] px-2 py-0.5 rounded-full font-medium uppercase tracking-wide",
                                            styles.labelBg,
                                            styles.labelText
                                        )}>
                                            {item.type}
                                        </span>
                                    </div>
                                    <h3 className="text-sm font-medium text-gray-900 mt-0.5 group-hover:text-primary-600 transition-colors">
                                        {item.title}
                                    </h3>
                                </div>
                            </motion.div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
}
