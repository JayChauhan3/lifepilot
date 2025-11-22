"use client";

import { motion } from "framer-motion";
import { FiTrendingUp, FiActivity, FiZap } from "react-icons/fi";

export default function SmartInsights() {
    return (
        <div className="bg-white rounded-2xl p-6 shadow-soft border border-gray-100">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Smart Insights</h2>

            <div className="space-y-4">
                <InsightItem
                    icon={FiTrendingUp}
                    color="emerald"
                    text="Your productivity was highest at 10–12 AM."
                    delay={0}
                />
                <InsightItem
                    icon={FiActivity}
                    color="rose"
                    text="You slept 1 hour less than your usual pattern."
                    delay={0.1}
                />
                <InsightItem
                    icon={FiZap}
                    color="amber"
                    text="You completed 74% of last week's goals."
                    delay={0.2}
                />
            </div>
        </div>
    );
}

function InsightItem({ icon: Icon, color, text, delay }: { icon: any, color: string, text: string, delay: number }) {
    return (
        <motion.div
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.5 + delay }}
            className="flex items-start gap-3 p-3 rounded-xl bg-gray-50 hover:bg-white hover:shadow-sm transition-all duration-200 border border-transparent hover:border-gray-100"
        >
            <div className={`p-2 rounded-lg bg-${color}-50 text-${color}-600 shrink-0`}>
                <Icon size={18} />
            </div>
            <p className="text-sm text-gray-700 leading-snug pt-1">
                {text}
            </p>
        </motion.div>
    );
}
