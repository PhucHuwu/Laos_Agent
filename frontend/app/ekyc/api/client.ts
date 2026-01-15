import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3724/api";

export const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        "Content-Type": "application/json",
    },
});

// Add session ID and JWT token to all requests
apiClient.interceptors.request.use((config) => {
    if (typeof window !== "undefined") {
        // Add session ID
        const sessionId = localStorage.getItem("sessionId");
        if (sessionId) {
            config.headers["X-Session-ID"] = sessionId;
        }

        // Add JWT token for authenticated requests
        const token = localStorage.getItem("auth_token");
        if (token) {
            config.headers["Authorization"] = `Bearer ${token}`;
        }
    }

    return config;
});

// Handle errors
apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem("sessionId");
        }
        return Promise.reject(error);
    }
);
