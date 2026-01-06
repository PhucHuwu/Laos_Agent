"use client"

import { useCallback } from "react"
import { useEKYCStore } from "../stores/ekyc-store"
import { useChatStore } from "../stores/chat-store"
import { verificationApi } from "../api/verification"
import type { VerificationResult } from "../types/verification"

export function useVerification() {
  const { idCardUrl, setVerificationResult, setProgress } = useEKYCStore()
  const { sessionId, addMessage } = useChatStore()

  const startVerification = useCallback(
    async (onProgress?: (similarity: number) => void) => {
      if (!idCardUrl || !sessionId) {
        throw new Error("ID card must be uploaded first")
      }

      setProgress("face_verifying")

      try {
        const response = await verificationApi.startVerification(idCardUrl, sessionId)

        if (response.success && response.data?.websocketUrl) {
          // Connect to WebSocket for realtime verification
          const ws = new WebSocket(response.data.websocketUrl)

          ws.onmessage = (event) => {
            try {
              const data = JSON.parse(event.data)

              if (data.type === "progress") {
                onProgress?.(data.similarity || 0)
              }

              if (data.type === "result") {
                const result: VerificationResult = {
                  samePerson: data.samePerson,
                  similarity: data.similarity,
                  confidence: data.confidence,
                  timestamp: new Date(),
                }

                setVerificationResult(result)
                setProgress("completed")

                addMessage({
                  id: Math.random().toString(36).slice(2),
                  role: "assistant",
                  content: data.samePerson
                    ? "Congratulations! Your identity has been verified successfully."
                    : "Verification failed. Please try again.",
                  timestamp: new Date(),
                })

                ws.close()
              }
            } catch (e) {
              console.error("WebSocket message error:", e)
            }
          }

          ws.onerror = () => {
            addMessage({
              id: Math.random().toString(36).slice(2),
              role: "assistant",
              content: "An error occurred during verification. Please try again.",
              timestamp: new Date(),
            })
          }

          return ws
        } else {
          throw new Error("Failed to start verification")
        }
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : "Verification failed"
        addMessage({
          id: Math.random().toString(36).slice(2),
          role: "assistant",
          content: `Error: ${errorMessage}`,
          timestamp: new Date(),
        })
        throw error
      }
    },
    [idCardUrl, sessionId, setProgress, setVerificationResult, addMessage],
  )

  return {
    startVerification,
  }
}
