'use client';

import ProtectedRoute from "@/components/auth/ProtectedRoute";
import PilotSummary from "@/components/dashboard/PilotSummary";
import TodayPlan from "@/components/dashboard/TodayPlan";
import TaskBoard from "@/components/dashboard/TaskBoard";
import SmartInsights from "@/components/dashboard/SmartInsights";
import NotificationsPanel from "@/components/dashboard/NotificationsPanel";

export default function Home() {

  return (
    <ProtectedRoute>
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
    </ProtectedRoute>
  );
}
