"use client"

import { useEKYCStore } from "../../stores/ekyc-store"

export function VerificationSummary() {
  const { scanResult, verificationResult } = useEKYCStore()

  if (!scanResult && !verificationResult) return null

  return (
    <div className="space-y-4 p-4 bg-card rounded-lg border border-border">
      {scanResult && (
        <div>
          <h4 className="font-semibold mb-3">ID Information</h4>
          <div className="grid grid-cols-2 gap-3">
            {scanResult.fields.idNumber && (
              <div>
                <p className="text-xs text-muted-foreground">ID Number</p>
                <p className="text-sm font-medium">{scanResult.fields.idNumber}</p>
              </div>
            )}
            {scanResult.fields.fullname && (
              <div>
                <p className="text-xs text-muted-foreground">Full Name</p>
                <p className="text-sm font-medium">{scanResult.fields.fullname}</p>
              </div>
            )}
            {scanResult.fields.dob && (
              <div>
                <p className="text-xs text-muted-foreground">Date of Birth</p>
                <p className="text-sm font-medium">{scanResult.fields.dob}</p>
              </div>
            )}
            {scanResult.fields.nationality && (
              <div>
                <p className="text-xs text-muted-foreground">Nationality</p>
                <p className="text-sm font-medium">{scanResult.fields.nationality}</p>
              </div>
            )}
          </div>
        </div>
      )}

      {verificationResult && (
        <div className="border-t border-border pt-4">
          <h4 className="font-semibold mb-3">Verification Result</h4>
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <p className="text-sm text-muted-foreground">Status</p>
              <span
                className={`px-2 py-1 rounded text-xs font-medium ${
                  verificationResult.samePerson
                    ? "bg-green-500/10 text-green-700 dark:text-green-400"
                    : "bg-red-500/10 text-red-700 dark:text-red-400"
                }`}
              >
                {verificationResult.samePerson ? "Verified" : "Failed"}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <p className="text-sm text-muted-foreground">Similarity</p>
              <p className="text-sm font-medium">{Math.round(verificationResult.similarity * 100)}%</p>
            </div>
            <div className="flex justify-between items-center">
              <p className="text-sm text-muted-foreground">Confidence</p>
              <p className="text-sm font-medium">{Math.round(verificationResult.confidence * 100)}%</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
