import { create } from "zustand";

interface UIState {
    uploadModalOpen: boolean;
    cameraModalOpen: boolean;
    resultModalOpen: boolean;
    sidebarOpen: boolean;

    openUploadModal: () => void;
    closeUploadModal: () => void;
    openCameraModal: () => void;
    closeCameraModal: () => void;
    openResultModal: () => void;
    closeResultModal: () => void;
    toggleSidebar: () => void;
    closeSidebar: () => void;
}

export const useUIStore = create<UIState>((set) => ({
    uploadModalOpen: false,
    cameraModalOpen: false,
    resultModalOpen: false,
    sidebarOpen: false,

    openUploadModal: () => set({ uploadModalOpen: true }),
    closeUploadModal: () => set({ uploadModalOpen: false }),
    openCameraModal: () => set({ cameraModalOpen: true }),
    closeCameraModal: () => set({ cameraModalOpen: false }),
    openResultModal: () => set({ resultModalOpen: true }),
    closeResultModal: () => set({ resultModalOpen: false }),
    toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
    closeSidebar: () => set({ sidebarOpen: false }),
}));
