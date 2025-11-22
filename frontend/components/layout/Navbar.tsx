import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useNotificationStore } from '@/store/notificationStore';

export const Navbar: React.FC = () => {
    const [showNotifications, setShowNotifications] = useState(false);
    const { notifications, connected, connect, markAsRead } = useNotificationStore();

    const unreadCount = notifications.filter(n => !n.read).length;

    // Connect to WebSocket on mount
    useEffect(() => {
        // Get or create user ID
        let userId = localStorage.getItem('lifepilot_user_id');
        if (!userId) {
            userId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
            localStorage.setItem('lifepilot_user_id', userId);
        }

        connect(userId);
    }, [connect]);

    const handleNotificationClick = (notifId: string) => {
        markAsRead(notifId);
    };

    return (
        <nav className="fixed top-0 left-0 right-0 z-50 bg-black/20 backdrop-blur-md border-b border-white/10">
            <div className="max-w-7xl mx-auto px-6 py-3">
                <div className="flex items-center justify-between">
                    {/* Logo */}
                    <Link href="/" className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-black rounded flex items-center justify-center">
                            <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                                <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
                            </svg>
                        </div>
                        <h1 className="text-xl font-bold text-white">LifePilot</h1>
                    </Link>

                    {/* Navigation Links */}
                    <div className="flex items-center space-x-6">
                        <Link
                            href="/"
                            className="text-gray-300 hover:text-white transition-colors"
                        >
                            Chat
                        </Link>
                        <Link
                            href="/dashboard"
                            className="text-gray-300 hover:text-white transition-colors"
                        >
                            Dashboard
                        </Link>

                        {/* Notification Bell */}
                        <div className="relative">
                            <button
                                onClick={() => setShowNotifications(!showNotifications)}
                                className="relative p-2 text-gray-300 hover:text-white hover:bg-white/10 rounded-lg transition-all"
                            >
                                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                                </svg>
                                {unreadCount > 0 && (
                                    <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                                        {unreadCount}
                                    </span>
                                )}
                                {/* Connection indicator */}
                                <span className={`absolute bottom-0 right-0 w-2 h-2 rounded-full ${connected ? 'bg-green-500' : 'bg-gray-500'}`}></span>
                            </button>

                            {/* Notification Dropdown */}
                            {showNotifications && (
                                <div className="absolute right-0 mt-2 w-80 bg-gray-900 border border-white/10 rounded-xl shadow-2xl overflow-hidden">
                                    <div className="p-4 border-b border-white/10">
                                        <h3 className="text-white font-semibold">Notifications</h3>
                                        {!connected && (
                                            <p className="text-xs text-yellow-400 mt-1">Reconnecting...</p>
                                        )}
                                    </div>
                                    <div className="max-h-96 overflow-y-auto">
                                        {notifications.length === 0 ? (
                                            <div className="p-8 text-center text-gray-400">
                                                No notifications yet
                                            </div>
                                        ) : (
                                            notifications.map((notif) => (
                                                <div
                                                    key={notif.id}
                                                    onClick={() => handleNotificationClick(notif.id)}
                                                    className={`p-4 border-b border-white/5 hover:bg-white/5 cursor-pointer ${!notif.read ? 'bg-blue-500/5' : ''
                                                        }`}
                                                >
                                                    <div className="flex items-start">
                                                        <div className={`mt-1 w-2 h-2 rounded-full mr-3 ${notif.priority === 'high'
                                                            ? 'bg-red-500'
                                                            : notif.priority === 'medium'
                                                                ? 'bg-yellow-500'
                                                                : 'bg-blue-500'
                                                            }`}></div>
                                                        <div className="flex-1">
                                                            <p className="text-sm text-white">{notif.message}</p>
                                                            <span className="text-xs text-gray-500 mt-1 block">
                                                                {new Date(notif.created_at).toLocaleTimeString()}
                                                            </span>
                                                        </div>
                                                    </div>
                                                </div>
                                            ))
                                        )}
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </nav>
    );
};
