"use client";

import ProductivityChart from "@/components/insights/ProductivityChart";
import { motion } from "framer-motion";
import { FiTrendingUp, FiZap, FiClock, FiCheckCircle } from "react-icons/fi";

export default function InsightsPage() {
    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-2xl font-bold text-gray-900 tracking-tight">Analytics & Insights</h1>
                <p className="text-gray-500 text-sm">Understand your productivity patterns</p>
            </div>

            {/* Key Metrics */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <MetricCard
                    title="Productivity Score"
                    value="78/100"
                    trend="+5%"
                    trendUp={true}
                    icon={FiTrendingUp}
                    color="blue"
                    delay={0}
                />
                <MetricCard
                    title="Tasks Completed"
                    value="24"
                    trend="+12%"
                    trendUp={true}
                    icon={FiCheckCircle}
                    color="emerald"
                    delay={0.1}
                />
                <MetricCard
                    title="Focus Time"
                    value="5h 30m"
                    trend="-30m"
                    trendUp={false}
                    icon={FiClock}
                    color="purple"
                    delay={0.2}
                />
                <MetricCard
                    title="Habit Streak"
                    value="12 Days"
                    trend="Best!"
                    trendUp={true}
                    icon={FiZap}
                    color="amber"
                    delay={0.3}
                />
            </div>

            {/* Charts */}
            <ProductivityChart />

            {/* AI Suggestions */}
            <div className="bg-gradient-to-br from-primary-600 to-primary-800 rounded-2xl p-6 sm:p-8 text-white shadow-lg relative overflow-hidden">
                <div className="absolute top-0 right-0 w-64 h-64 bg-white rounded-full blur-3xl -translate-y-1/2 translate-x-1/3 opacity-10" />

                <div className="relative z-10">
                    <div className="flex items-center gap-3 mb-4">
                        <div className="p-2 bg-white/20 rounded-lg backdrop-blur-sm">
                            <FiZap className="text-yellow-300" size={24} />
                        </div>
                        <h2 className="text-xl font-bold">AI Optimization Suggestion</h2>
                    </div>

                    <p className="text-primary-100 text-lg leading-relaxed max-w-2xl">
                        "Based on your patterns, you are most productive between 10 AM and 12 PM.
                        Try scheduling your deep work blocks during this time to increase output by ~20%."
                    </p>

                    <div className="mt-6 flex gap-3">
                        <button className="px-5 py-2.5 bg-white text-primary-700 font-semibold rounded-lg hover:bg-primary-50 transition-colors shadow-sm">
                            Apply to Schedule
                        </button>
                        <button className="px-5 py-2.5 bg-primary-700/50 text-white font-medium rounded-lg hover:bg-primary-700 transition-colors backdrop-blur-sm">
                            Dismiss
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}

function MetricCard({ title, value, trend, trendUp, icon: Icon, color, delay }: any) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: delay * 0.1 }}
            className="bg-white p-5 rounded-2xl shadow-soft border border-gray-100"
        >
            <div className="flex items-start justify-between mb-4">
                <div className={`p-2 rounded-lg bg-${color}-50 text-${color}-600`}>
                    <Icon size={20} />
                </div>
                <span className={`text-xs font-bold px-2 py-1 rounded-full ${trendUp ? 'bg-green-50 text-green-600' : 'bg-rose-50 text-rose-600'
                    }`}>
                    {trend}
                </span>
            </div>
            <h3 className="text-gray-500 text-sm font-medium">{title}</h3>
            <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
        </motion.div>
    );
}
