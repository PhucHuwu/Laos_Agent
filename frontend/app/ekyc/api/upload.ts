import { apiClient } from "./client";
import type { UploadResponse, ApiResponse } from "../types/api";

export const uploadApi = {
    uploadIdCard: async (file: File, onProgress?: (progress: number) => void) => {
        const formData = new FormData();
        formData.append("file", file);

        const response = await apiClient.post<{
            success: boolean;
            image_url?: string;
            scan_result?: any;
            formatted_html?: string;
            message?: string;
            id_card_url?: string;
            auto_open_camera?: boolean;
            error?: string;
        }>("/upload", formData, {
            headers: {
                "Content-Type": "multipart/form-data",
            },
            onUploadProgress: (event: { loaded: number; total?: number }) => {
                if (event.total && onProgress) {
                    const progress = (event.loaded / event.total) * 100;
                    onProgress(progress);
                }
            },
        });

        return response.data;
    },
};
