/**
 * Authentication API functions
 */

import { apiClient } from "./client";

interface AuthResponse {
    access_token: string;
    token_type: string;
    user_id: string;
    is_verified: boolean;
}

interface RegisterData {
    phone: string;
    password: string;
    full_name?: string;
}

interface LoginData {
    phone: string;
    password: string;
}

const TOKEN_KEY = "auth_token";
const USER_KEY = "auth_user";

/**
 * Register a new user
 */
export async function register(data: RegisterData): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>("/auth/register", data);

    // Save token and user info
    saveAuthData(response.data);

    return response.data;
}

/**
 * Login with phone and password
 */
export async function login(data: LoginData): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>("/auth/login", data);

    // Save token and user info
    saveAuthData(response.data);

    return response.data;
}

/**
 * Logout - clear stored auth data
 */
export function logout(): void {
    if (typeof window !== "undefined") {
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(USER_KEY);
        localStorage.removeItem("sessionId"); // Clear chat session ID
    }
}

/**
 * Get stored token
 */
export function getToken(): string | null {
    if (typeof window !== "undefined") {
        return localStorage.getItem(TOKEN_KEY);
    }
    return null;
}

/**
 * Get stored user info
 */
export function getStoredUser(): { id: string; phone: string; isVerified: boolean } | null {
    if (typeof window !== "undefined") {
        const userStr = localStorage.getItem(USER_KEY);
        if (userStr) {
            try {
                return JSON.parse(userStr);
            } catch {
                return null;
            }
        }
    }
    return null;
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
    return !!getToken();
}

/**
 * Save auth data to localStorage
 */
function saveAuthData(data: AuthResponse): void {
    if (typeof window !== "undefined") {
        localStorage.setItem(TOKEN_KEY, data.access_token);
        localStorage.setItem(
            USER_KEY,
            JSON.stringify({
                id: data.user_id,
                isVerified: data.is_verified,
            })
        );
    }
}
