"use client";

import Link from "next/link";
import Image from "next/image";
import { usePathname, useRouter } from "next/navigation";
import {
    FiHome,
    FiMessageSquare,
    FiCheckSquare,
    FiPieChart,
    FiSettings,
    FiMenu,
    FiLogOut
} from "react-icons/fi";
import { motion } from "framer-motion";
import clsx from "clsx";
import { useState, useEffect } from "react";
import { authService } from "@/services/authService";

const NAV_ITEMS = [
    { name: "Dashboard", href: "/", icon: FiHome },
    { name: "Planner", href: "/planner", icon: FiMessageSquare },
    { name: "Tasks & Routines", href: "/tasks", icon: FiCheckSquare },
    { name: "Insights", href: "/insights", icon: FiPieChart },
    { name: "Settings", href: "/settings", icon: FiSettings },
];

export default function Sidebar() {
    const pathname = usePathname();
    const router = useRouter();
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
    const [user, setUser] = useState<{ email: string; full_name?: string } | null>(null);

    useEffect(() => {
        // Fetch current user info
        const fetchUser = async () => {
            try {
                const userData = await authService.getCurrentUser();
                setUser(userData);
            } catch (error) {
                console.error('Failed to fetch user:', error);
            }
        };

        if (authService.isAuthenticated()) {
            fetchUser();
        }
    }, []);

    const handleLogout = () => {
        authService.logout();
        router.push('/login');
    };

    // Get user initials
    const getInitials = () => {
        if (user?.full_name) {
            return user.full_name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
        }
        if (user?.email) {
            return user.email.slice(0, 2).toUpperCase();
        }
        return 'U';
    };

    return (
        <>
            {/* Mobile Menu Button */}
            <div className="lg:hidden fixed top-4 left-4 z-50">
                <button
                    onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                    className="p-2 bg-white rounded-lg shadow-md text-gray-600 hover:text-primary-600 transition-colors"
                >
                    <FiMenu size={24} />
                </button>
            </div>

            {/* Sidebar Container */}
            <aside
                className={clsx(
                    "fixed top-0 left-0 z-40 h-screen w-64 bg-white border-r border-gray-100 transition-transform duration-300 ease-in-out lg:translate-x-0",
                    isMobileMenuOpen ? "translate-x-0 shadow-2xl" : "-translate-x-full"
                )}
            >
                <div className="flex flex-col h-full">
                    {/* Logo Section */}
                    <div className="h-16 flex items-center px-6 border-b border-gray-50">
                        <div className="flex items-center gap-3">
                            <Image
                                src="/images/logo.png"
                                alt="LifePilot Logo"
                                width={32}
                                height={32}
                                className="object-contain"
                                priority
                            />
                            <span className="text-xl font-bold text-gray-900 tracking-tight">LifePilot</span>
                        </div>
                    </div>

                    {/* Navigation Links */}
                    <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
                        {NAV_ITEMS.map((item) => {
                            const isActive = pathname === item.href;
                            const Icon = item.icon;

                            return (
                                <Link
                                    key={item.name}
                                    href={item.href}
                                    onClick={() => setIsMobileMenuOpen(false)}
                                    className={clsx(
                                        "relative flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 group",
                                        isActive
                                            ? "text-primary-700 bg-primary-50"
                                            : "text-gray-700 hover:text-gray-900 hover:bg-gray-50"
                                    )}
                                >
                                    {isActive && (
                                        <motion.span
                                            layoutId="activeNav"
                                            className="absolute left-0 w-1 h-8 bg-primary-600 rounded-r-full"
                                            initial={{ opacity: 0 }}
                                            animate={{ opacity: 1 }}
                                            exit={{ opacity: 0 }}
                                        />
                                    )}
                                    <Icon
                                        size={20}
                                        className={clsx(
                                            "transition-colors duration-200",
                                            isActive ? "text-primary-600" : "text-gray-500 group-hover:text-gray-700"
                                        )}
                                    />
                                    {item.name}
                                </Link>
                            );
                        })}
                    </nav>

                    {/* User Profile / Footer */}
                    <div className="p-4 border-t border-gray-50 space-y-2">
                        {/* User Info */}
                        <div className="flex items-center gap-3 px-2 py-2 rounded-lg hover:bg-gray-50 transition-colors">
                            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-primary-500 to-purple-500 flex items-center justify-center text-white text-xs font-bold">
                                {getInitials()}
                            </div>
                            <div className="flex-1 min-w-0">
                                <p className="text-sm font-medium text-gray-900 truncate">
                                    {user?.full_name || user?.email || 'Loading...'}
                                </p>
                                <p className="text-xs text-gray-500 truncate">
                                    {user?.email && user?.full_name ? user.email : 'Pro Plan'}
                                </p>
                            </div>
                        </div>

                        {/* Logout Button */}
                        <button
                            onClick={handleLogout}
                            className="w-full flex items-center gap-3 px-4 py-2 rounded-lg text-sm font-medium text-red-600 hover:bg-red-50 transition-colors"
                        >
                            <FiLogOut size={18} />
                            Logout
                        </button>
                    </div>
                </div>
            </aside>

            {/* Mobile Overlay */}
            {isMobileMenuOpen && (
                <div
                    className="fixed inset-0 z-30 bg-black/20 backdrop-blur-sm lg:hidden"
                    onClick={() => setIsMobileMenuOpen(false)}
                />
            )}
        </>
    );
}
