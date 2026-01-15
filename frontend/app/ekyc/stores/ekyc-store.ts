import { create } from "zustand";
import type { ScanResult, VerificationResult } from "../types/verification";

// Flow: idle → id_uploading → id_scanned → face_verifying → verified → idle
type Progress = "idle" | "id_uploading" | "id_scanned" | "face_verifying" | "verified";

interface EKYCState {
    progress: Progress;
    idCardUrl: string | null;
    scanResult: ScanResult | null;
    verificationResult: VerificationResult | null;

    setProgress: (p: Progress) => void;
    setIdCardUrl: (url: string) => void;
    setScanResult: (result: ScanResult) => void;
    setVerificationResult: (result: VerificationResult) => void;
    reset: () => void;
}

export const useEKYCStore = create<EKYCState>((set) => ({
    progress: "idle",
    idCardUrl: null,
    scanResult: null,
    verificationResult: null,

    setProgress: (p) => set({ progress: p }),
    setIdCardUrl: (url) => set({ idCardUrl: url }),
    setScanResult: (result) => set({ scanResult: result }),
    setVerificationResult: (result) => set({ verificationResult: result }),
    reset: () =>
        set({
            progress: "idle",
            idCardUrl: null,
            scanResult: null,
            verificationResult: null,
        }),
}));
