"use client"

import { CheckCircle, AlertCircle } from "lucide-react"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { useUIStore } from "../../stores/ui-store"
import { useEKYCStore } from "../../stores/ekyc-store"

interface ResultModalProps {
  type: "success" | "error"
  title: string
  message: string
}

export function ResultModal({ type, title, message }: ResultModalProps) {
  const { resultModalOpen, closeResultModal } = useUIStore()
  const { verificationResult } = useEKYCStore()

  const isSuccess = type === "success"

  return (
    <Dialog open={resultModalOpen} onOpenChange={closeResultModal}>
      <DialogContent className="sm:max-w-md text-center">
        <DialogHeader>
          <DialogTitle className="text-center">{title}</DialogTitle>
        </DialogHeader>

        <div className="flex justify-center py-4">
          {isSuccess ? (
            <CheckCircle className="w-16 h-16 text-green-600" />
          ) : (
            <AlertCircle className="w-16 h-16 text-red-600" />
          )}
        </div>

        <p className="text-sm text-muted-foreground mb-4">{message}</p>

        {verificationResult && (
          <div className="bg-muted rounded-lg p-4 text-left space-y-2 mb-4">
            <div className="flex justify-between text-sm">
              <span>Similarity:</span>
              <strong>{Math.round(verificationResult.similarity * 100)}%</strong>
            </div>
            <div className="flex justify-between text-sm">
              <span>Confidence:</span>
              <strong>{Math.round(verificationResult.confidence * 100)}%</strong>
            </div>
          </div>
        )}

        <Button onClick={closeResultModal} className="w-full">
          {isSuccess ? "Continue" : "Try Again"}
        </Button>
      </DialogContent>
    </Dialog>
  )
}
