export interface ScanResult {
    document_type: string;
    display_name: string;
    text?: string[];
    fields: {
        id_number?: string;
        fullname?: string;
        dob?: string;
        gender?: string;
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
    img_url?: string;
    img_base64?: string;
}

export interface VerificationResult {
    samePerson: boolean;
    similarity: number;
    confidence: number;
    bbox?: number[];
    faceImage?: string;
    timestamp: Date;
}

export interface UploadProgress {
    loaded: number;
    total: number;
}
