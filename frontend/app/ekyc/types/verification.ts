export interface ScanResult {
  documentType: string
  confidence: number
  fields: {
    idNumber?: string
    fullname?: string
    dob?: string
    gender?: string
    nationality?: string
    expiryDate?: string
  }
  rawImage?: string
}

export interface VerificationResult {
  samePerson: boolean
  similarity: number
  confidence: number
  bbox?: number[]
  faceImage?: string
  timestamp: Date
}

export interface UploadProgress {
  loaded: number
  total: number
}
