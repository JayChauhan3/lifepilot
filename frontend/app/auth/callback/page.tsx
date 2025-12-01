'use client';

import { Suspense, useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { authService } from '@/services/authService';

function AuthCallbackContent() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
    const [message, setMessage] = useState('Processing authentication...');

    useEffect(() => {
        const handleCallback = async () => {
            try {
                // Get token from URL
                const token = searchParams.get('token');

                if (!token) {
                    setStatus('error');
                    setMessage('No authentication token received');
                    setTimeout(() => router.push('/login'), 3000);
                    return;
                }

                // Store token
                authService.setToken(token);

                // Verify token by getting user
                await authService.getCurrentUser();

                // Redirect immediately to home
                router.push('/');
            } catch (error: any) {
                setStatus('error');
                setMessage(error.message || 'Authentication failed');
                setTimeout(() => router.push('/login'), 3000);
            }
        };

        handleCallback();
    }, [searchParams, router]);

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 p-4">
            <div className="w-full max-w-md">
                <div className="bg-white/10 backdrop-blur-xl rounded-2xl shadow-2xl p-8 border border-white/20 text-center">
                    {/* Status Icon */}
                    <div className="mb-6">
                        {status === 'loading' && (
                            <div className="inline-block">
                                <div className="w-16 h-16 border-4 border-blue-400 border-t-transparent rounded-full animate-spin"></div>
                            </div>
                        )}
                        {status === 'success' && (
                            <div className="inline-flex items-center justify-center w-16 h-16 bg-green-500/20 rounded-full">
                                <svg className="w-10 h-10 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                </svg>
                            </div>
                        )}
                        {status === 'error' && (
                            <div className="inline-flex items-center justify-center w-16 h-16 bg-red-500/20 rounded-full">
                                <svg className="w-10 h-10 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                </svg>
                            </div>
                        )}
                    </div>

                    {/* Message */}
                    <h2 className="text-2xl font-bold text-white mb-2">
                        {status === 'loading' && 'Authenticating...'}
                        {status === 'success' && 'Success!'}
                        {status === 'error' && 'Authentication Failed'}
                    </h2>
                    <p className="text-blue-200">{message}</p>

                    {/* Progress Bar */}
                    {status === 'loading' && (
                        <div className="mt-6 w-full bg-white/10 rounded-full h-2 overflow-hidden">
                            <div className="h-full bg-gradient-to-r from-blue-500 to-purple-600 animate-pulse"></div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default function AuthCallbackPage() {
    return (
        <Suspense fallback={
            <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 p-4">
                <div className="w-16 h-16 border-4 border-blue-400 border-t-transparent rounded-full animate-spin"></div>
            </div>
        }>
            <AuthCallbackContent />
        </Suspense>
    );
}
