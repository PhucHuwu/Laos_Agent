"use client"

import { useEffect, useRef, useCallback } from "react"

interface UseWebSocketOptions {
  onMessage?: (data: any) => void
  onError?: (error: Error) => void
  onClose?: () => void
}

export function useWebSocket(url: string | null, options: UseWebSocketOptions = {}) {
  const wsRef = useRef<WebSocket | null>(null)
  const { onMessage, onError, onClose } = options

  useEffect(() => {
    if (!url) return

    try {
      wsRef.current = new WebSocket(url)

      wsRef.current.onopen = () => {
        console.log("[WebSocket] Connected")
      }

      wsRef.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          onMessage?.(data)
        } catch (e) {
          console.error("[WebSocket] Parse error:", e)
        }
      }

      wsRef.current.onerror = (event) => {
        const error = new Error("WebSocket error")
        onError?.(error)
      }

      wsRef.current.onclose = () => {
        onClose?.()
      }
    } catch (error) {
      onError?.(error instanceof Error ? error : new Error("WebSocket connection failed"))
    }

    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [url, onMessage, onError, onClose])

  const send = useCallback((data: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data))
    }
  }, [])

  return { send, ws: wsRef.current }
}
