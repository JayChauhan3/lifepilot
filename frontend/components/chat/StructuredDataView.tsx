import React from 'react';
import { DashboardView } from '@/components/widgets/DashboardView';
import { NotificationList } from '@/components/widgets/NotificationList';

interface StructuredDataViewProps {
    data: any;
    type?: string; // 'dashboard', 'notification_list', 'analysis'
}

export const StructuredDataView: React.FC<StructuredDataViewProps> = ({ data, type }) => {
    if (!data) return null;

    // Determine type if not provided
    const viewType = type || (data.widgets ? 'dashboard' : (Array.isArray(data) ? 'notification_list' : 'unknown'));

    return (
        <div className="mt-4 w-full">
            {viewType === 'dashboard' && (
                <DashboardView data={data} />
            )}

            {viewType === 'notification_list' && (
                <NotificationList alerts={data} />
            )}

            {viewType === 'analysis' && (
                <div className="bg-gray-800/50 border border-white/10 rounded-xl p-4">
                    <h3 className="text-sm font-medium text-gray-400 mb-2 uppercase tracking-wider">Analysis</h3>
                    <pre className="text-xs text-gray-300 overflow-x-auto whitespace-pre-wrap">
                        {JSON.stringify(data, null, 2)}
                    </pre>
                </div>
            )}

            {/* Legacy Shopping List Support */}
            {data.items && Array.isArray(data.items) && !viewType.startsWith('notification') && (
                <div className="space-y-3">
                    {data.items.map((category: any, index: number) => (
                        <div key={index} className="bg-white/5 rounded-xl p-3 border border-white/10">
                            <h4 className="font-medium text-white mb-2">{category.category}</h4>
                            <div className="flex flex-wrap gap-2">
                                {category.items.map((item: string, itemIndex: number) => (
                                    <span
                                        key={itemIndex}
                                        className="inline-flex items-center px-3 py-1 rounded-lg text-sm bg-white/10 border border-white/20 text-gray-300"
                                    >
                                        {item}
                                    </span>
                                ))}
                            </div>
                        </div>
                    ))}
                    {data.totalItems && (
                        <div className="text-sm text-gray-400 border-t border-white/10 pt-2">
                            Total items: {data.totalItems}
                        </div>
                    )}
                    {data.estimatedCost && (
                        <div className="text-sm text-gray-400">
                            Estimated cost: {data.estimatedCost}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};
