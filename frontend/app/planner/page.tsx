"use client";

import ProtectedRoute from "@/components/auth/ProtectedRoute";
import ChatInterface from "@/components/planner/ChatInterface";
import AgentActionsPanel from "@/components/planner/AgentActionsPanel";

export default function PlannerPage() {
    return (
        <ProtectedRoute>
            <div className="h-[calc(100vh-8rem)]">
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 h-full">
                    {/* Left Column: Chat Interface (8 cols) */}
                    <div className="lg:col-span-8 h-full">
                        <ChatInterface />
                    </div>

                    {/* Right Column: Agent Actions (4 cols) */}
                    <div className="lg:col-span-4 h-full">
                        <AgentActionsPanel />
                    </div>
                </div>
            </div>
        </ProtectedRoute>
    );
}
