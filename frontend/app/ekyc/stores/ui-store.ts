import { create } from "zustand"

interface UIState {
  uploadModalOpen: boolean
  cameraModalOpen: boolean
  resultModalOpen: boolean

  openUploadModal: () => void
  closeUploadModal: () => void
  openCameraModal: () => void
  closeCameraModal: () => void
  openResultModal: () => void
  closeResultModal: () => void
}

export const useUIStore = create<UIState>((set) => ({
  uploadModalOpen: false,
  cameraModalOpen: false,
  resultModalOpen: false,

  openUploadModal: () => set({ uploadModalOpen: true }),
  closeUploadModal: () => set({ uploadModalOpen: false }),
  openCameraModal: () => set({ cameraModalOpen: true }),
  closeCameraModal: () => set({ cameraModalOpen: false }),
  openResultModal: () => set({ resultModalOpen: true }),
  closeResultModal: () => set({ resultModalOpen: false }),
}))
