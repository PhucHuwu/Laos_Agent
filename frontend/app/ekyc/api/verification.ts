import type { ApiResponse, VerificationStartResponse } from "../types/api";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export const verificationApi = {
    startVerification: async (idCardImageUrl: string, sessionId: string) => {
        const response = await fetch(`${API_BASE_URL}/start-ws-verification`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-Session-ID": sessionId,
            },
            body: JSON.stringify({ id_card_image_url: idCardImageUrl }),
        });

        if (!response.ok) throw new Error("Failed to start verification");
        return await response.json();
    },

    // Send frame via HTTP POST (not WebSocket)
    sendFrame: async (frameBase64: string, sessionId: string) => {
        const response = await fetch(`${API_BASE_URL}/send-frame`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-Session-ID": sessionId,
            },
            body: JSON.stringify({ frame_base64: frameBase64 }),
        });

        if (!response.ok) throw new Error("Failed to send frame");
        return await response.json();
    },

    stopVerification: async (sessionId: string) => {
        const response = await fetch(`${API_BASE_URL}/stop-ws-verification`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-Session-ID": sessionId,
            },
        });

        if (!response.ok) throw new Error("Failed to stop verification");
        return await response.json();
    },
};
