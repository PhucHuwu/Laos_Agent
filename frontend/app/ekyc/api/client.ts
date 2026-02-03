import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3724/api";

// Generate or get session ID
function getSessionId(): string {
    if (typeof window === "undefined") return "";

    let sessionId = localStorage.getItem("session_id");
    if (!sessionId) {
        sessionId = crypto.randomUUID();
        localStorage.setItem("session_id", sessionId);
    }
    return sessionId;
}

export const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        "Content-Type": "application/json",
    },
});

// Add session ID to all requests
apiClient.interceptors.request.use((config) => {
    if (typeof window !== "undefined") {
        const sessionId = getSessionId();
        if (sessionId) {
            config.headers["X-Session-ID"] = sessionId;
        }
    }
    return config;
});

// Handle errors
apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        return Promise.reject(error);
    },
);

export { getSessionId };
