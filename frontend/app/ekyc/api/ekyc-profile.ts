import { apiClient } from "./client";

export interface EKYCProfileResponse {
    success: boolean;
    is_verified: boolean;
    id_card_image_url?: string;
    selfie_image_url?: string;
    ocr_data?: {
        text?: string;
        document_type?: string;
        display_name?: string;
        fields?: {
            id_number?: string;
            fullname?: string;
            dob?: string;
            nationality?: string;
            ethnicity?: string;
            address?: {
                address: string;
                childrent?: {
                    address_village?: string;
                    address_district?: string;
                    address_province?: string;
                };
            };
            issue_date?: string;
            expiry_date?: string;
        };
        raw_data?: {
            img_url?: string;
            fields?: any;
        };
    };
    face_match_score?: number;
    verified_at?: string;
    error?: string;
}

export const ekycProfileApi = {
    getProfile: async (): Promise<EKYCProfileResponse> => {
        const response = await apiClient.get<EKYCProfileResponse>("/ekyc/profile");
        return response.data;
    },
};
