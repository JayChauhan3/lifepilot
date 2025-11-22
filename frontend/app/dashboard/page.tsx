'use client'

import React from 'react'
import { Navbar } from '@/components/layout/Navbar'
import { NotificationToaster } from '@/components/notifications/NotificationToaster'

export default function DashboardPage() {
    return (
        <>
            <Navbar />
            <NotificationToaster />
            <div className="min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-900 pt-20 px-6">
                <div className="max-w-7xl mx-auto">
                    <h1 className="text-3xl font-bold text-white mb-8">Dashboard</h1>

                    {/* Dashboard Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

                        {/* Today's Schedule */}
                        <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-6">
                            <h2 className="text-xl font-semibold text-white mb-4">Today's Schedule</h2>
                            <div className="space-y-3">
                                <div className="bg-black/20 p-3 rounded-lg">
                                    <div className="flex justify-between items-start">
                                        <div>
                                            <p className="text-white font-medium">Team Standup</p>
                                            <p className="text-gray-400 text-sm">9:00 AM - 9:30 AM</p>
                                        </div>
                                        <span className="bg-blue-500/20 text-blue-400 text-xs px-2 py-1 rounded">Soon</span>
                                    </div>
                                </div>
                                <div className="bg-black/20 p-3 rounded-lg">
                                    <div className="flex justify-between items-start">
                                        <div>
                                            <p className="text-white font-medium">Client Meeting</p>
                                            <p className="text-gray-400 text-sm">2:00 PM - 3:00 PM</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Active Tasks */}
                        <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-6">
                            <h2 className="text-xl font-semibold text-white mb-4">Active Tasks</h2>
                            <div className="space-y-2">
                                <div className="flex items-center justify-between bg-black/20 p-3 rounded-lg">
                                    <span className="text-white">Review PRs</span>
                                    <span className="bg-yellow-500/20 text-yellow-400 text-xs px-2 py-1 rounded">High</span>
                                </div>
                                <div className="flex items-center justify-between bg-black/20 p-3 rounded-lg">
                                    <span className="text-white">Update docs</span>
                                    <span className="bg-green-500/20 text-green-400 text-xs px-2 py-1 rounded">Medium</span>
                                </div>
                                <div className="flex items-center justify-between bg-black/20 p-3 rounded-lg">
                                    <span className="text-white">Team sync prep</span>
                                    <span className="bg-blue-500/20 text-blue-400 text-xs px-2 py-1 rounded">Low</span>
                                </div>
                            </div>
                        </div>

                        {/* Weather */}
                        <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-6">
                            <h2 className="text-xl font-semibold text-white mb-4">Weather</h2>
                            <div className="flex items-center justify-between">
                                <div>
                                    <div className="text-5xl font-bold text-white">22°C</div>
                                    <div className="text-gray-400 mt-2">Partly Cloudy</div>
                                </div>
                                <div className="text-6xl">🌤️</div>
                            </div>
                            <div className="mt-4 pt-4 border-t border-white/10">
                                <div className="flex justify-between text-sm">
                                    <span className="text-gray-400">Humidity</span>
                                    <span className="text-white">65%</span>
                                </div>
                                <div className="flex justify-between text-sm mt-2">
                                    <span className="text-gray-400">Wind</span>
                                    <span className="text-white">12 km/h</span>
                                </div>
                            </div>
                        </div>

                        {/* Productivity Stats */}
                        <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-6 md:col-span-2">
                            <h2 className="text-xl font-semibold text-white mb-4">This Week</h2>
                            <div className="grid grid-cols-3 gap-4">
                                <div className="text-center">
                                    <div className="text-3xl font-bold text-blue-400">12</div>
                                    <div className="text-gray-400 text-sm mt-1">Tasks Done</div>
                                </div>
                                <div className="text-center">
                                    <div className="text-3xl font-bold text-green-400">8</div>
                                    <div className="text-gray-400 text-sm mt-1">Meetings</div>
                                </div>
                                <div className="text-center">
                                    <div className="text-3xl font-bold text-purple-400">85%</div>
                                    <div className="text-gray-400 text-sm mt-1">Productivity</div>
                                </div>
                            </div>
                        </div>

                        {/* Quick Actions */}
                        <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-6">
                            <h2 className="text-xl font-semibold text-white mb-4">Quick Actions</h2>
                            <div className="space-y-2">
                                <button className="w-full bg-blue-500/20 hover:bg-blue-500/30 text-blue-400 py-2 px-4 rounded-lg transition-colors text-left">
                                    + Add Task
                                </button>
                                <button className="w-full bg-green-500/20 hover:bg-green-500/30 text-green-400 py-2 px-4 rounded-lg transition-colors text-left">
                                    📅 Schedule Meeting
                                </button>
                                <button className="w-full bg-purple-500/20 hover:bg-purple-500/30 text-purple-400 py-2 px-4 rounded-lg transition-colors text-left">
                                    📊 View Analytics
                                </button>
                            </div>
                        </div>

                    </div>
                </div>
            </div>
        </>
    )
}
