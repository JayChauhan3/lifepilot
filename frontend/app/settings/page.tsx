"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { FiUser, FiZap, FiCpu, FiSave, FiToggleRight, FiToggleLeft } from "react-icons/fi";
import clsx from "clsx";

export default function SettingsPage() {
    return (
        <div className="max-w-4xl mx-auto space-y-8 pb-12">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 tracking-tight">Settings & Memory</h1>
                    <p className="text-gray-500 text-sm">Manage what LifePilot knows about you</p>
                </div>
                <button className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition-colors shadow-sm">
                    <FiSave size={18} />
                    Save Changes
                </button>
            </div>

            {/* Personal Preferences */}
            <SettingsSection
                title="Personal Preferences"
                icon={FiUser}
                description="Basic information to tailor your experience"
                delay={0}
            >
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <InputField label="Wake Time" defaultValue="07:00 AM" type="time" />
                    <InputField label="Sleep Time" defaultValue="11:00 PM" type="time" />
                    <SelectField label="Dietary Preference" defaultValue="Non-veg" options={["Veg", "Non-veg", "Vegan", "Keto"]} />
                    <SelectField label="Exercise Preference" defaultValue="Gym" options={["Gym", "Running", "Yoga", "Home Workout"]} />
                    <InputField label="Work Hours Start" defaultValue="09:00 AM" type="time" />
                    <InputField label="Work Hours End" defaultValue="06:00 PM" type="time" />
                </div>
            </SettingsSection>

            {/* Productivity Settings */}
            <SettingsSection
                title="Productivity Settings"
                icon={FiZap}
                description="Optimize how tasks and schedules are managed"
                delay={0.1}
            >
                <div className="space-y-4">
                    <ToggleField label="Enable Smart Notifications" description="Get nudged when you're off track" defaultChecked={true} />
                    <ToggleField label="Auto-schedule Deep Work" description="Automatically block time for focused work" defaultChecked={true} />
                    <ToggleField label="Energy Level Optimization" description="Schedule hard tasks during peak energy hours" defaultChecked={true} />

                    <div className="pt-2">
                        <label className="block text-sm font-medium text-gray-700 mb-2">Focus Block Duration</label>
                        <div className="flex gap-3">
                            {["25m", "45m", "60m", "90m"].map((duration) => (
                                <button
                                    key={duration}
                                    className={clsx(
                                        "px-4 py-2 rounded-lg text-sm font-medium border transition-all",
                                        duration === "60m"
                                            ? "bg-primary-50 border-primary-200 text-primary-700"
                                            : "bg-white border-gray-200 text-gray-600 hover:border-gray-300"
                                    )}
                                >
                                    {duration}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>
            </SettingsSection>

            {/* Agent Preferences */}
            <SettingsSection
                title="Agent Preferences"
                icon={FiCpu}
                description="Control autonomy levels for each agent"
                delay={0.2}
            >
                <div className="space-y-4">
                    <AgentToggle
                        name="Planner Agent"
                        desc="Can modify your calendar without asking"
                        defaultChecked={false}
                        color="blue"
                    />
                    <AgentToggle
                        name="Routine Loop Agent"
                        desc="Can trigger routines automatically"
                        defaultChecked={true}
                        color="purple"
                    />
                    <AgentToggle
                        name="Task Executor"
                        desc="Can add tasks from emails/messages"
                        defaultChecked={true}
                        color="emerald"
                    />
                    <AgentToggle
                        name="Knowledge Agent"
                        desc="Can browse web for context"
                        defaultChecked={true}
                        color="amber"
                    />
                </div>
            </SettingsSection>
        </div>
    );
}

function SettingsSection({ title, icon: Icon, description, children, delay }: any) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: delay * 0.1 }}
            className="bg-white rounded-2xl p-6 sm:p-8 shadow-soft border border-gray-100"
        >
            <div className="flex items-start gap-4 mb-8">
                <div className="p-3 bg-gray-50 rounded-xl text-gray-600">
                    <Icon size={24} />
                </div>
                <div>
                    <h2 className="text-xl font-bold text-gray-900">{title}</h2>
                    <p className="text-gray-500 text-sm mt-1">{description}</p>
                </div>
            </div>
            {children}
        </motion.div>
    );
}

function InputField({ label, defaultValue, type = "text" }: any) {
    return (
        <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">{label}</label>
            <input
                type={type}
                defaultValue={defaultValue}
                className="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all text-gray-900"
            />
        </div>
    );
}

function SelectField({ label, defaultValue, options }: any) {
    return (
        <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">{label}</label>
            <div className="relative">
                <select
                    defaultValue={defaultValue}
                    className="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all text-gray-900 appearance-none"
                >
                    {options.map((opt: string) => (
                        <option key={opt} value={opt}>{opt}</option>
                    ))}
                </select>
                <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-gray-400">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path></svg>
                </div>
            </div>
        </div>
    );
}

function ToggleField({ label, description, defaultChecked }: any) {
    const [enabled, setEnabled] = useState(defaultChecked);

    return (
        <div className="flex items-center justify-between py-2">
            <div>
                <h3 className="text-sm font-medium text-gray-900">{label}</h3>
                <p className="text-xs text-gray-500 mt-0.5">{description}</p>
            </div>
            <button
                onClick={() => setEnabled(!enabled)}
                className={clsx(
                    "relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2",
                    enabled ? "bg-primary-600" : "bg-gray-200"
                )}
            >
                <span className={clsx(
                    "inline-block h-4 w-4 transform rounded-full bg-white transition-transform",
                    enabled ? "translate-x-6" : "translate-x-1"
                )} />
            </button>
        </div>
    );
}

function AgentToggle({ name, desc, defaultChecked, color }: any) {
    const [enabled, setEnabled] = useState(defaultChecked);

    return (
        <div className="flex items-center justify-between p-4 rounded-xl border border-gray-100 bg-gray-50/50">
            <div className="flex items-center gap-3">
                <div className={`w-2 h-2 rounded-full bg-${color}-500`} />
                <div>
                    <h3 className="text-sm font-bold text-gray-900">{name}</h3>
                    <p className="text-xs text-gray-500">{desc}</p>
                </div>
            </div>
            <button
                onClick={() => setEnabled(!enabled)}
                className={clsx(
                    "relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2",
                    enabled ? `bg-${color}-500` : "bg-gray-200"
                )}
            >
                <span className={clsx(
                    "inline-block h-4 w-4 transform rounded-full bg-white transition-transform",
                    enabled ? "translate-x-6" : "translate-x-1"
                )} />
            </button>
        </div>
    );
}
