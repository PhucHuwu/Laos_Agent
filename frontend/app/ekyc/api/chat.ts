import { apiClient } from "./client";
import type { ChatResponse, ApiResponse } from "../types/api";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3724/api";

export const chatApi = {
    sendMessage: async (message: string) => {
        const response = await apiClient.post<{
            success: boolean;
            response?: string;
            tool_calls?: any[];
            error?: string;
        }>("/chat", { message });
        return response.data;
    },

    resetConversation: async () => {
        const response = await apiClient.post<{
            success: boolean;
            message: string;
        }>("/reset");
        return response.data;
    },

    getHistory: async () => {
        const response = await apiClient.get<{
            success: boolean;
            messages: any[];
            context?: any;
            progress?: string;
            error?: string;
        }>("/chat/history");
        return response.data;
    },

    clearHistory: async () => {
        const response = await apiClient.delete<{
            success: boolean;
            error?: string;
        }>("/chat/history");
        return response.data;
    },

    // Streaming chat using fetch with POST (SSE)
    async *streamChat(message: string): AsyncGenerator<any, void, unknown> {
        // Get session ID from localStorage
        let sessionId = typeof window !== "undefined" ? localStorage.getItem("session_id") : null;
        if (!sessionId && typeof window !== "undefined") {
            sessionId = crypto.randomUUID();
            localStorage.setItem("session_id", sessionId);
        }

        const response = await fetch(`${API_BASE_URL}/chat-stream`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                ...(sessionId ? { "X-Session-ID": sessionId } : {}),
            },
            body: JSON.stringify({ message }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body?.getReader();
        if (!reader) {
            throw new Error("No reader available");
        }

        const decoder = new TextDecoder();
        let buffer = "";

        try {
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split("\n");
                buffer = lines.pop() || "";

                for (const line of lines) {
                    if (line.startsWith("data: ")) {
                        const data = line.slice(6).trim();
                        if (data === "[DONE]") {
                            return;
                        }
                        try {
                            const parsed = JSON.parse(data);
                            yield parsed;
                        } catch (e) {
                            // Skip invalid JSON
                        }
                    }
                }
            }
        } finally {
            reader.releaseLock();
        }
    },
};
