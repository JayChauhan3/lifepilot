"use client";

import { usePathname } from "next/navigation";
import Sidebar from "./Sidebar";

export default function AppLayout({ children }: { children: React.ReactNode }) {
    const pathname = usePathname();

    // Don't show sidebar on auth pages
    const isAuthPage = pathname === '/login' || pathname === '/register' || pathname?.startsWith('/auth/');

    if (isAuthPage) {
        return <>{children}</>;
    }

    return (
        <div className="min-h-screen bg-white">
            <Sidebar />
            <main className="lg:pl-64 min-h-screen transition-all duration-300">
                <div className="max-w-7xl mx-auto p-4 sm:p-6 lg:p-8">
                    {children}
                </div>
            </main>
        </div>
    );
}
