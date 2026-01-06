"use client"

import { CheckCircle, Circle } from "lucide-react"
import { useEKYCStore } from "../../stores/ekyc-store"

export function VerificationProgress() {
  const { progress } = useEKYCStore()

  const steps = [
    { id: "id_uploaded", label: "Upload ID", description: "Provide your ID card" },
    { id: "id_scanned", label: "Scan ID", description: "Extract information" },
    { id: "face_verifying", label: "Face Verification", description: "Verify your identity" },
    { id: "completed", label: "Completed", description: "Verification done" },
  ]

  const currentStepIndex = steps.findIndex((s) => s.id === progress)

  return (
    <div className="w-full px-4 py-6 bg-card border-b border-border">
      <div className="max-w-4xl mx-auto">
        <h3 className="text-sm font-semibold mb-4">Verification Progress</h3>
        <div className="flex items-center justify-between relative">
          {/* Progress line */}
          <div className="absolute top-4 left-0 right-0 h-1 bg-muted">
            <div
              className="h-full bg-primary transition-all duration-300"
              style={{
                width: currentStepIndex >= 0 ? `${(currentStepIndex / (steps.length - 1)) * 100}%` : "0%",
              }}
            />
          </div>

          {/* Steps */}
          <div className="relative flex justify-between w-full">
            {steps.map((step, index) => {
              const isCompleted = currentStepIndex > index
              const isCurrent = currentStepIndex === index
              const isUpcoming = index > currentStepIndex

              return (
                <div key={step.id} className="flex flex-col items-center gap-2">
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center border-2 transition-all ${
                      isCompleted
                        ? "bg-primary border-primary text-primary-foreground"
                        : isCurrent
                          ? "bg-primary/10 border-primary text-primary"
                          : "bg-muted border-border text-muted-foreground"
                    }`}
                  >
                    {isCompleted ? <CheckCircle className="w-5 h-5" /> : <Circle className="w-5 h-5" />}
                  </div>
                  <div className="text-center">
                    <p className="text-xs font-medium">{step.label}</p>
                    <p className="text-xs text-muted-foreground hidden md:block">{step.description}</p>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </div>
  )
}
