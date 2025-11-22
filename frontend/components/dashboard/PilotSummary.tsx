"use client";

import { motion } from "framer-motion";
import { FiSun, FiCheckCircle, FiTarget, FiCloud } from "react-icons/fi";

export default function PilotSummary() {
    const summaryItems = [
        { icon: FiCheckCircle, text: "Day fully planned", checked: true },
        { icon: FiTarget, text: "Tasks synced", checked: true },
        { icon: FiCloud, text: "Weather checked", checked: true },
        { icon: FiCheckCircle, text: "Alerts scheduled", checked: true },
    ];

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="bg-white rounded-2xl p-6 sm:p-8 shadow-soft border border-gray-100 relative overflow-hidden"
        >
            {/* Background Decoration */}
            <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-primary-50 to-purple-50 rounded-full blur-3xl -translate-y-1/2 translate-x-1/3 opacity-60" />

            <div className="relative z-10">
                <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-6">
                    {/* Greeting & Goal */}
                    <div className="space-y-4 max-w-xl">
                        <div>
                            <div className="flex items-center gap-2 text-gray-500 text-sm font-medium mb-1">
                                <FiSun className="text-amber-500" />
                                <span>Good Evening, Jay</span>
                            </div>
                            <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 tracking-tight">
                                Ready to conquer the day?
                            </h1>
                        </div>

                        <div className="bg-primary-50/50 border border-primary-100 rounded-xl p-4 flex items-start gap-3">
                            <div className="p-2 bg-white rounded-lg shadow-sm text-primary-600">
                                <FiTarget size={20} />
                            </div>
                            <div>
                                <h3 className="text-sm font-semibold text-primary-900">Today's Focus</h3>
                                <p className="text-primary-700 text-sm mt-0.5">
                                    Work blocks, hydration, and workout.
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* Planner Summary */}
                    <div className="bg-gray-50 rounded-xl p-5 border border-gray-100 min-w-[240px]">
                        <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
                            Planner Agent Summary
                        </h3>
                        <div className="space-y-2.5">
                            {summaryItems.map((item, index) => (
                                <motion.div
                                    key={index}
                                    initial={{ opacity: 0, x: 10 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: 0.2 + index * 0.1 }}
                                    className="flex items-center gap-2.5 text-sm text-gray-700"
                                >
                                    <div className="text-green-500">
                                        <item.icon size={16} />
                                    </div>
                                    <span>{item.text}</span>
                                </motion.div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </motion.div>
    );
}
