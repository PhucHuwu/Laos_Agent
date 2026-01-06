"use client"

import { useEffect, useCallback } from "react"
import { useChatStore } from "../stores/chat-store"
import { useEKYCStore } from "../stores/ekyc-store"
import { generateSessionId } from "../utils/formatters"

export function useSession() {
  const { sessionId, setSessionId } = useChatStore()
  const { progress, reset: resetEKYC } = useEKYCStore()

  useEffect(() => {
    // Initialize session from localStorage or create new one
    const storedSessionId = typeof window !== "undefined" ? localStorage.getItem("sessionId") : null

    if (storedSessionId) {
      setSessionId(storedSessionId)
    } else {
      const newSessionId = generateSessionId()
      localStorage.setItem("sessionId", newSessionId)
      setSessionId(newSessionId)
    }
  }, [setSessionId])

  const resetSession = useCallback(() => {
    const newSessionId = generateSessionId()
    localStorage.setItem("sessionId", newSessionId)
    setSessionId(newSessionId)
    resetEKYC()
  }, [setSessionId, resetEKYC])

  const clearSession = useCallback(() => {
    localStorage.removeItem("sessionId")
  }, [])

  return {
    sessionId,
    resetSession,
    clearSession,
  }
}
