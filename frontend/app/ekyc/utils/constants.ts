export const EKYC_STEPS = {
  UPLOAD_ID: "upload_id",
  SCAN_ID: "scan_id",
  FACE_VERIFY: "face_verify",
  COMPLETED: "completed",
} as const

export const API_ENDPOINTS = {
  CHAT: "/chat",
  UPLOAD: "/upload/id-card",
  VERIFY: "/verification",
  VERIFY_START: "/verification/start",
} as const

export const ERROR_MESSAGES = {
  CAMERA_NOT_AVAILABLE: "Camera is not available on this device",
  UPLOAD_FAILED: "Failed to upload ID card",
  VERIFICATION_FAILED: "Face verification failed",
  NETWORK_ERROR: "Network error, please try again",
} as const

export const SUCCESS_MESSAGES = {
  ID_UPLOADED: "ID card uploaded successfully",
  ID_SCANNED: "ID card scanned successfully",
  FACE_VERIFIED: "Face verification successful",
  PROCESS_COMPLETE: "eKYC process completed successfully",
} as const
