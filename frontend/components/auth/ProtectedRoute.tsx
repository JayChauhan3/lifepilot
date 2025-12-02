'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { authService } from '@/services/authService';

interface ProtectedRouteProps {
    children: React.ReactNode;
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
    const router = useRouter();
    const [isVerifying, setIsVerifying] = useState(true);
    const [isAuthenticated, setIsAuthenticated] = useState(false);

    useEffect(() => {
        const verifyAuth = async () => {
            try {
                // First check if token exists
                if (!authService.isAuthenticated()) {
                    router.push('/login');
                    return;
                }

                // Verify token is valid by fetching current user
                await authService.getCurrentUser();
                setIsAuthenticated(true);
            } catch (error) {
                // Token is invalid or expired, redirect to login
                authService.removeToken();
                router.push('/login');
            } finally {
                setIsVerifying(false);
            }
        };

        verifyAuth();
    }, [router]);

    // Show loading spinner during verification
    if (isVerifying) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
            </div>
        );
    }

    // Only render children if authenticated
    return isAuthenticated ? <>{children}</> : null;
}
