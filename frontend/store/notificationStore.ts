import { create } from 'zustand';
import toast from 'react-hot-toast';

interface Notification {
    id: string;
    message: string;
    priority: 'low' | 'medium' | 'high';
    created_at: string;
    read: boolean;
}

interface NotificationStore {
    notifications: Notification[];
    ws: WebSocket | null;
    connected: boolean;

    // Actions
    connect: (userId: string) => void;
    disconnect: () => void;
    addNotification: (notification: Notification) => void;
    markAsRead: (notificationId: string) => void;
    clearAll: () => void;
}

export const useNotificationStore = create<NotificationStore>((set, get) => ({
    notifications: [],
    ws: null,
    connected: false,

    connect: (userId: string) => {
        const ws = new WebSocket(`ws://localhost:8000/ws/notifications/${userId}`);

        ws.onopen = () => {
            console.log('WebSocket connected');
            set({ connected: true });
            // Removed annoying toast notification on connect
        };

        ws.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);
                if (message.type === 'notification') {
                    const notification = message.data;

                    // Add to store
                    set((state) => ({
                        notifications: [notification, ...state.notifications]
                    }));

                    // Show toast
                    const toastMessage = notification.message;
                    if (notification.priority === 'high') {
                        toast.error(toastMessage, { duration: 8000 });
                    } else if (notification.priority === 'medium') {
                        toast(toastMessage, {
                            icon: '⚠️',
                            duration: 6000
                        });
                    } else {
                        toast.success(toastMessage);
                    }
                }
            } catch (error) {
                console.error('Failed to parse WebSocket message:', error);
            }
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            toast.error('Notification connection error');
        };

        ws.onclose = () => {
            console.log('WebSocket disconnected');
            set({ connected: false, ws: null });

            // Attempt to reconnect after 5 seconds
            setTimeout(() => {
                if (!get().connected) {
                    console.log('Attempting to reconnect...');
                    get().connect(userId);
                }
            }, 5000);
        };

        set({ ws });
    },

    disconnect: () => {
        const { ws } = get();
        if (ws) {
            ws.close();
            set({ ws: null, connected: false });
        }
    },

    addNotification: (notification) => {
        set((state) => ({
            notifications: [notification, ...state.notifications]
        }));
    },

    markAsRead: (notificationId) => {
        set((state) => ({
            notifications: state.notifications.map((n) =>
                n.id === notificationId ? { ...n, read: true } : n
            )
        }));
    },

    clearAll: () => {
        set({ notifications: [] });
    },
}));
