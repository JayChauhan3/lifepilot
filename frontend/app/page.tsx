'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { authService } from '@/services/authService';
import PilotSummary from "@/components/dashboard/PilotSummary";
import TodayPlan from "@/components/dashboard/TodayPlan";
import TaskBoard from "@/components/dashboard/TaskBoard";
import SmartInsights from "@/components/dashboard/SmartInsights";
import NotificationsPanel from "@/components/dashboard/NotificationsPanel";

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    // Check if user is authenticated
    if (!authService.isAuthenticated()) {
      router.push('/login');
    }
  }, [router]);

  // Don't render dashboard if not authenticated
  if (!authService.isAuthenticated()) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Hero Section */}
      <section>
        <PilotSummary />
      </section>

      {/* Main Grid Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Timeline (4 cols) */}
        <div className="lg:col-span-4 h-full">
          <TodayPlan />
        </div>

        {/* Middle Column: Task Board (5 cols) */}
        <div className="lg:col-span-5 h-full">
          <TaskBoard />
        </div>

        {/* Right Column: Insights & Notifications (3 cols) */}
        <div className="lg:col-span-3 space-y-6 flex flex-col h-full">
          <div className="shrink-0">
            <SmartInsights />
          </div>
          <div className="flex-1 min-h-[300px]">
            <NotificationsPanel />
          </div>
        </div>
      </div>
    </div>
  );
}
