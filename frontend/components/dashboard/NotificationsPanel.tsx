"use client";

import { motion } from "framer-motion";
import { FiBell, FiClock, FiInfo } from "react-icons/fi";

export default function NotificationsPanel() {
    const notifications = [
        { id: 1, title: "Meeting in 15m", desc: "Design Review", type: "urgent", time: "Now" },
        { id: 2, title: "Routine Completed", desc: "Morning Routine", type: "success", time: "2h ago" },
        { id: 3, title: "New Insight", desc: "Weekly report ready", type: "info", time: "4h ago" },
    ];

    return (
        <div className="bg-white rounded-2xl p-6 shadow-soft border border-gray-100 h-full">
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                    <FiBell className="text-primary-600" />
                    <h2 className="text-lg font-bold text-gray-900">Updates</h2>
                </div>
                <span className="text-xs font-medium bg-primary-50 text-primary-700 px-2 py-1 rounded-full">
                    3 New
                </span>
            </div>

            <div className="space-y-3">
                {notifications.map((notif, index) => (
                    <motion.div
                        key={notif.id}
                        initial={{ opacity: 0, x: 10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.6 + index * 0.1 }}
                        className="flex items-start gap-3 p-3 rounded-xl hover:bg-gray-50 transition-colors border-b border-gray-50 last:border-0"
                    >
                        <div className={`w-2 h-2 mt-2 rounded-full shrink-0 ${notif.type === 'urgent' ? 'bg-rose-500' :
                            notif.type === 'success' ? 'bg-emerald-500' : 'bg-blue-500'
                            }`} />

                        <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-gray-900 truncate">{notif.title}</p>
                            <p className="text-xs text-gray-500 truncate">{notif.desc}</p>
                        </div>

                        <span className="text-[10px] text-gray-400 whitespace-nowrap">
                            {notif.time}
                        </span>
                    </motion.div>
                ))}
            </div>
        </div>
    );
}
