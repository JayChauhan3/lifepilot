import React from 'react';

interface DashboardData {
    layout: string;
    widgets: Array<{
        id: string;
        type: string;
        title: string;
        data: any;
        size: string;
    }>;
}

interface DashboardViewProps {
    data: DashboardData;
}

export const DashboardView: React.FC<DashboardViewProps> = ({ data }) => {
    if (!data || !data.widgets) return null;

    return (
        <div className="w-full mt-4 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {data.widgets.map((widget) => (
                    <div
                        key={widget.id}
                        className={`bg-gray-800/50 border border-white/10 rounded-xl p-4 ${widget.size === 'large' ? 'md:col-span-2' : ''
                            }`}
                    >
                        <h3 className="text-sm font-medium text-gray-400 mb-3 uppercase tracking-wider">
                            {widget.title}
                        </h3>

                        {widget.type === 'weather' && (
                            <div className="flex items-center justify-between">
                                <div>
                                    <div className="text-4xl font-bold text-white">{widget.data.temperature}°C</div>
                                    <div className="text-gray-400">{widget.data.condition}</div>
                                </div>
                                <div className="text-right">
                                    <div className="text-sm text-gray-400">Humidity: {widget.data.humidity}%</div>
                                    <div className="text-sm text-gray-400">Wind: {widget.data.wind_speed} km/h</div>
                                </div>
                            </div>
                        )}

                        {widget.type === 'task_list' && (
                            <div className="space-y-2">
                                {widget.data.tasks.map((task: string, idx: number) => (
                                    <div key={idx} className="flex items-center justify-between bg-black/20 p-2 rounded">
                                        <span className="text-white">{task}</span>
                                        <span className="bg-yellow-500/20 text-yellow-400 text-xs px-2 py-1 rounded">
                                            Pending
                                        </span>
                                    </div>
                                ))}
                            </div>
                        )}

                        {widget.type === 'daily_plan' && (
                            <div className="space-y-3">
                                <div className="text-white text-sm">{widget.data.summary}</div>
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
};
