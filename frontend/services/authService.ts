const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface LoginCredentials {
    email: string;
    password: string;
}

export interface RegisterData {
    email: string;
    password: string;
    full_name?: string;
}

export interface AuthResponse {
    access_token: string;
    token_type: string;
}

export interface User {
    user_id: string;
    email: string;
    full_name?: string;
    is_active: boolean;
    is_verified: boolean;
}

class AuthService {
    private readonly TOKEN_KEY = 'lifepilot_token';

    // Store token in localStorage
    setToken(token: string): void {
        if (typeof window !== 'undefined') {
            localStorage.setItem(this.TOKEN_KEY, token);
        }
    }

    // Get token from localStorage
    getToken(): string | null {
        if (typeof window !== 'undefined') {
            return localStorage.getItem(this.TOKEN_KEY);
        }
        return null;
    }

    // Remove token from localStorage
    removeToken(): void {
        if (typeof window !== 'undefined') {
            localStorage.removeItem(this.TOKEN_KEY);
        }
    }

    // Check if user is authenticated
    isAuthenticated(): boolean {
        return this.getToken() !== null;
    }

    // Register new user
    async register(data: RegisterData): Promise<User> {
        const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Registration failed');
        }

        return response.json();
    }

    // Login with email and password
    async login(credentials: LoginCredentials): Promise<AuthResponse> {
        const formData = new URLSearchParams();
        formData.append('username', credentials.email);
        formData.append('password', credentials.password);

        const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData,
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Login failed');
        }

        const data: AuthResponse = await response.json();
        this.setToken(data.access_token);
        return data;
    }

    // Login with Google OAuth
    loginWithGoogle(): void {
        window.location.href = `${API_BASE_URL}/api/auth/google/login`;
    }

    // Logout
    logout(): void {
        this.removeToken();
    }

    // Get current user
    async verifyEmail(email: string, code: string): Promise<AuthResponse> {
        const response = await fetch(`${API_BASE_URL}/api/auth/verify`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, code }),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Verification failed');
        }

        const data = await response.json();
        this.setToken(data.access_token);
        return data;
    }

    async getCurrentUser(): Promise<User> {
        const token = this.getToken();
        if (!token) {
            throw new Error('Not authenticated');
        }

        const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });

        if (!response.ok) {
            if (response.status === 401) {
                this.removeToken();
                throw new Error('Session expired');
            }
            throw new Error('Failed to get user');
        }

        return response.json();
    }

    // Get auth headers for API requests
    getAuthHeaders(): HeadersInit {
        const token = this.getToken();
        if (!token) {
            return {};
        }

        return {
            'Authorization': `Bearer ${token}`,
        };
    }
}

export const authService = new AuthService();
