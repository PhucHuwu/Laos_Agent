"use client"

import { useEKYCStore } from "../../stores/ekyc-store"
import { X } from "lucide-react"
import { Button } from "@/components/ui/button"

interface IdCardDisplayProps {
  onRemove?: () => void
}

export function IdCardDisplay({ onRemove }: IdCardDisplayProps) {
  const { idCardUrl } = useEKYCStore()

  if (!idCardUrl) return null

  return (
    <div className="relative rounded-lg overflow-hidden border border-border">
      <img src={idCardUrl || "/placeholder.svg"} alt="ID Card" className="w-full h-auto" />
      {onRemove && (
        <Button
          variant="destructive"
          size="sm"
          onClick={onRemove}
          className="absolute top-2 right-2"
          aria-label="Remove ID card"
        >
          <X className="w-4 h-4" />
        </Button>
      )}
    </div>
  )
}
