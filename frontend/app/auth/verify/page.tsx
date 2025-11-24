'use client';

import { useEffect, useState, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { authService } from '@/services/authService';
import Link from 'next/link';

function VerifyContent() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const [status, setStatus] = useState<'verifying' | 'success' | 'error'>('verifying');
    const [message, setMessage] = useState('Verifying your email...');

    useEffect(() => {
        const verify = async () => {
            const email = searchParams.get('email');
            const code = searchParams.get('code');

            if (!email || !code) {
                setStatus('error');
                setMessage('Invalid verification link. Missing email or code.');
                return;
            }

            try {
                await authService.verifyEmail(email, code);
                setStatus('success');
                setMessage('Email verified successfully! Redirecting to login...');
                setTimeout(() => {
                    router.push('/login?verified=true');
                }, 2000);
            } catch (error: any) {
                setStatus('error');
                setMessage(error.message || 'Verification failed. Please try again.');
            }
        };

        verify();
    }, [searchParams, router]);

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-md w-full space-y-8 bg-white p-8 rounded-lg shadow-md">
                <div className="text-center">
                    <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
                        Email Verification
                    </h2>
                    <div className="mt-4">
                        {status === 'verifying' && (
                            <div className="flex justify-center">
                                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
                            </div>
                        )}
                        {status === 'success' && (
                            <div className="text-green-600">
                                <svg className="mx-auto h-12 w-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                </svg>
                            </div>
                        )}
                        {status === 'error' && (
                            <div className="text-red-600">
                                <svg className="mx-auto h-12 w-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                </svg>
                            </div>
                        )}
                        <p className={`mt-4 text-lg ${status === 'error' ? 'text-red-600' :
                            status === 'success' ? 'text-green-600' :
                                'text-gray-600'
                            }`}>
                            {message}
                        </p>
                        {status === 'error' && (
                            <div className="mt-6">
                                <Link href="/auth/login" className="text-indigo-600 hover:text-indigo-500 font-medium">
                                    Back to Login
                                </Link>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}

export default function VerifyPage() {
    return (
        <Suspense fallback={<div>Loading...</div>}>
            <VerifyContent />
        </Suspense>
    );
}
