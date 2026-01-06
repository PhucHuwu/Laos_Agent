export interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: string
  message?: string
}

export interface ChatRequest {
  message: string
  sessionId: string
}

export interface ChatResponse {
  id: string
  role: string
  content: string
  toolCalls?: Array<{
    id: string
    name: string
    arguments: Record<string, any>
  }>
}

export interface UploadResponse {
  url: string
  scanResult: any
}

export interface VerificationStartResponse {
  websocketUrl: string
  sessionId: string
}
