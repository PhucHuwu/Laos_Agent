/**
 * Authentication state store using Zustand
 */

import { create } from "zustand";
import * as authApi from "../api/auth";
import { useChatStore } from "./chat-store";

interface User {
    id: string;
    phone?: string;
    isVerified: boolean;
}

interface AuthState {
    user: User | null;
    token: string | null;
    isAuthenticated: boolean;
    isInitialized: boolean; // Flag to track if auth check is done
    isLoading: boolean;
    error: string | null;

    // Actions
    login: (phone: string, password: string) => Promise<boolean>;
    register: (phone: string, password: string, fullName?: string) => Promise<boolean>;
    logout: () => void;
    checkAuth: () => void;
    clearError: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
    user: null,
    token: null,
    isAuthenticated: false,
    isInitialized: false,
    isLoading: false,
    error: null,

    login: async (phone: string, password: string) => {
        set({ isLoading: true, error: null });
        try {
            const response = await authApi.login({ phone, password });
            set({
                user: { id: response.user_id, isVerified: response.is_verified },
                token: response.access_token,
                isAuthenticated: true,
                isLoading: false,
            });
            return true;
        } catch (error: any) {
            const message = error.response?.data?.detail || "ການເຂົ້າສູ່ລະບົບລົ້ມເຫລວ";
            set({ error: message, isLoading: false });
            return false;
        }
    },

    register: async (phone: string, password: string, fullName?: string) => {
        set({ isLoading: true, error: null });
        try {
            const response = await authApi.register({ phone, password, full_name: fullName });
            set({
                user: { id: response.user_id, isVerified: response.is_verified },
                token: response.access_token,
                isAuthenticated: true,
                isLoading: false,
            });
            return true;
        } catch (error: any) {
            const message = error.response?.data?.detail || "ການລົງທະບຽນລົ້ມເຫລວ";
            set({ error: message, isLoading: false });
            return false;
        }
    },

    logout: () => {
        authApi.logout();
        useChatStore.getState().reset(); // Reset chat state
        set({
            user: null,
            token: null,
            isAuthenticated: false,
            error: null,
        });
    },

    checkAuth: () => {
        const token = authApi.getToken();
        const user = authApi.getStoredUser();
        if (token && user) {
            set({
                user,
                token,
                isAuthenticated: true,
                isInitialized: true,
            });
        } else {
            set({ isInitialized: true });
        }
    },

    clearError: () => set({ error: null }),
}));
