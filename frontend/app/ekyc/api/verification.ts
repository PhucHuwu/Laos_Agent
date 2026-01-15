import { apiClient } from "./client";
import type { ApiResponse, VerificationStartResponse } from "../types/api";

export const verificationApi = {
    // SessionID is now handled by backend via Auth Token, keeping arg for compatibility for now but ignoring it
    startVerification: async (idCardImageUrl: string, sessionId?: string) => {
        const response = await apiClient.post("/start-ws-verification", {
            id_card_image_url: idCardImageUrl,
        });
        return response.data;
    },

    // Send frame via HTTP POST (not WebSocket)
    sendFrame: async (frameBase64: string, sessionId?: string) => {
        const response = await apiClient.post("/send-frame", {
            frame_base64: frameBase64,
        });
        return response.data;
    },

    stopVerification: async (sessionId?: string) => {
        const response = await apiClient.post("/stop-ws-verification");
        return response.data;
    },
};
