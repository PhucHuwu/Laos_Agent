"use client"

import { useRef, useCallback, useState } from "react"

export function useCamera() {
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [error, setError] = useState<string | null>(null)

  const startCamera = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: "user",
        },
      })

      if (videoRef.current) {
        videoRef.current.srcObject = stream
      }

      setError(null)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to access camera"
      setError(errorMessage)
      console.error("Camera error:", err)
    }
  }, [])

  const stopCamera = useCallback(() => {
    if (videoRef.current?.srcObject) {
      const tracks = (videoRef.current.srcObject as MediaStream).getTracks()
      tracks.forEach((track) => track.stop())
    }
  }, [])

  const captureFrame = useCallback(() => {
    if (!videoRef.current) return ""

    const canvas = canvasRef.current || document.createElement("canvas")
    const ctx = canvas.getContext("2d")

    if (!ctx) return ""

    canvas.width = videoRef.current.videoWidth
    canvas.height = videoRef.current.videoHeight

    ctx.drawImage(videoRef.current, 0, 0)
    return canvas.toDataURL("image/jpeg", 0.8)
  }, [])

  return {
    videoRef,
    startCamera,
    stopCamera,
    captureFrame,
    error,
  }
}
