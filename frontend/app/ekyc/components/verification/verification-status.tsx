"use client"

import { CheckCircle, AlertCircle, Clock } from "lucide-react"
import { useEKYCStore } from "../../stores/ekyc-store"

interface VerificationStatusProps {
  showDetails?: boolean
}

export function VerificationStatus({ showDetails = true }: VerificationStatusProps) {
  const { progress, verificationResult } = useEKYCStore()

  let status: "pending" | "success" | "error" = "pending"
  let message = ""

  if (progress === "completed" && verificationResult?.samePerson) {
    status = "success"
    message = "Your identity has been verified successfully!"
  } else if (verificationResult && !verificationResult.samePerson) {
    status = "error"
    message = "Verification failed. Please try again."
  } else if (progress === "face_verifying") {
    status = "pending"
    message = "Verifying your identity..."
  }

  return (
    <div
      className={`rounded-lg p-4 border ${
        status === "success"
          ? "bg-green-50 dark:bg-green-950/20 border-green-200 dark:border-green-800"
          : status === "error"
            ? "bg-red-50 dark:bg-red-950/20 border-red-200 dark:border-red-800"
            : "bg-blue-50 dark:bg-blue-950/20 border-blue-200 dark:border-blue-800"
      }`}
    >
      <div className="flex items-start gap-3">
        {status === "success" && (
          <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
        )}
        {status === "error" && <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />}
        {status === "pending" && <Clock className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />}

        <div>
          <p
            className={`font-medium ${
              status === "success"
                ? "text-green-900 dark:text-green-100"
                : status === "error"
                  ? "text-red-900 dark:text-red-100"
                  : "text-blue-900 dark:text-blue-100"
            }`}
          >
            {message}
          </p>

          {showDetails && verificationResult && (
            <p className="text-sm text-muted-foreground mt-1">
              Similarity: {Math.round(verificationResult.similarity * 100)}% | Confidence:{" "}
              {Math.round(verificationResult.confidence * 100)}%
            </p>
          )}
        </div>
      </div>
    </div>
  )
}
