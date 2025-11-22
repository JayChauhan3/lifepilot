import React from 'react';

interface Alert {
    id: string;
    message: string;
    priority: 'low' | 'medium' | 'high';
    created_at: string;
    status: string;
}

interface NotificationListProps {
    alerts: Alert[];
}

export const NotificationList: React.FC<NotificationListProps> = ({ alerts }) => {
    if (!alerts || alerts.length === 0) return null;

    return (
        <div className="w-full mt-4 space-y-2">
            <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-2">
                Notifications
            </h3>
            {alerts.map((alert) => (
                <div
                    key={alert.id}
                    className={`flex items-start p-3 rounded-lg border ${alert.priority === 'high'
                            ? 'bg-red-500/10 border-red-500/30'
                            : alert.priority === 'medium'
                                ? 'bg-yellow-500/10 border-yellow-500/30'
                                : 'bg-blue-500/10 border-blue-500/30'
                        }`}
                >
                    <div className={`mt-1 w-2 h-2 rounded-full mr-3 ${alert.priority === 'high'
                            ? 'bg-red-500'
                            : alert.priority === 'medium'
                                ? 'bg-yellow-500'
                                : 'bg-blue-500'
                        }`}></div>
                    <div className="flex-1">
                        <p className="text-sm text-white">{alert.message}</p>
                        <span className="text-xs text-gray-500 mt-1 block">
                            {new Date(alert.created_at).toLocaleTimeString()}
                        </span>
                    </div>
                </div>
            ))}
        </div>
    );
};
