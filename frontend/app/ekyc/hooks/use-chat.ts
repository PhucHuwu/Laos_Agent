"use client"

import { useCallback, useState } from "react"
import { useChatStore } from "../stores/chat-store"
import { useEKYCStore } from "../stores/ekyc-store"
import { useUIStore } from "../stores/ui-store"
import { chatApi } from "../api/chat"
import type { Message } from "../types/chat"

export function useChat() {
  const { messages, addMessage, setLoading, isLoading, sessionId } = useChatStore()
  const { idCardUrl } = useEKYCStore()
  const { openUploadModal, openCameraModal } = useUIStore()
  const [error, setError] = useState<string | null>(null)

  const sendMessage = useCallback(
    async (content: string) => {
      if (!sessionId || !content.trim()) return

      // Add user message
      const userMessage: Message = {
        id: Math.random().toString(36).slice(2),
        role: "user",
        content: content.trim(),
        timestamp: new Date(),
      }

      addMessage(userMessage)
      setLoading(true)
      setError(null)

      try {
        const response = await chatApi.sendMessage(content, sessionId)

        if (response.success && response.data) {
          const assistantMessage: Message = {
            id: Math.random().toString(36).slice(2),
            role: "assistant",
            content: response.data.content,
            timestamp: new Date(),
            toolCalls: response.data.toolCalls,
          }

          addMessage(assistantMessage)

          // Handle tool calls
          if (response.data.toolCalls) {
            for (const toolCall of response.data.toolCalls) {
              await handleToolCall(toolCall.name, toolCall.arguments)
            }
          }
        } else {
          throw new Error(response.error || "Failed to send message")
        }
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : "An error occurred"
        setError(errorMessage)

        const errorMessage_msg: Message = {
          id: Math.random().toString(36).slice(2),
          role: "assistant",
          content: `Sorry, there was an error: ${errorMessage}`,
          timestamp: new Date(),
        }

        addMessage(errorMessage_msg)
      } finally {
        setLoading(false)
      }
    },
    [sessionId, addMessage, setLoading],
  )

  const handleToolCall = async (toolName: string, args: Record<string, any>) => {
    switch (toolName) {
      case "upload_id_card":
        openUploadModal()
        break
      case "start_face_verification":
        if (idCardUrl) {
          openCameraModal()
        } else {
          sendMessage("Please upload your ID card first")
        }
        break
      case "get_verification_status":
        sendMessage("Checking your verification status...")
        break
      default:
        console.warn(`Unknown tool: ${toolName}`)
    }
  }

  return {
    sendMessage,
    messages,
    isLoading,
    error,
  }
}
