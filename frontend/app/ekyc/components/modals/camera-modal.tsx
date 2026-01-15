"use client";

import { useState, useEffect, useRef } from "react";
import { Camera, CheckCircle, XCircle } from "lucide-react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { ProgressBar } from "../ui/progress-bar";
import { useUIStore } from "../../stores/ui-store";
import { useEKYCStore } from "../../stores/ekyc-store";
import { useChatStore } from "../../stores/chat-store";
import { useCamera } from "../../hooks/use-camera";
import { verificationApi } from "../../api/verification";

export function CameraModal() {
    const { cameraModalOpen, closeCameraModal } = useUIStore();
    const { idCardUrl, setVerificationResult, setProgress, reset: resetEKYC } = useEKYCStore();
    const { addMessage, reset: resetChat } = useChatStore();

    const { videoRef, startCamera, stopCamera, captureFrame } = useCamera();
    const [isVerifying, setIsVerifying] = useState(false);
    const [similarity, setSimilarity] = useState(0);
    const [status, setStatus] = useState<"idle" | "capturing" | "success" | "failed">("idle");
    const intervalRef = useRef<NodeJS.Timeout | null>(null);

    useEffect(() => {
        if (cameraModalOpen) {
            startCamera();
            setStatus("idle");
            setSimilarity(0);
        }

        return () => {
            stopCamera();
            if (intervalRef.current) {
                clearInterval(intervalRef.current);
            }
        };
    }, [cameraModalOpen, startCamera, stopCamera]);

    const handleStartVerification = async () => {
        if (!idCardUrl) {
            alert("ກະລຸນາອັບໂຫລດບັດປະຈຳຕົວກ່ອນ");
            return;
        }

        setIsVerifying(true);
        setStatus("capturing");
        setProgress("face_verifying");

        try {
            // Start WebSocket verification
            const startResult = await verificationApi.startVerification(idCardUrl);
            console.log("Start verification result:", startResult);

            if (!startResult.success) {
                throw new Error(startResult.error || "Failed to start verification");
            }

            // Send frames periodically
            let frameCount = 0;
            const maxFrames = 300; // Max 300 frames (about 60 seconds at 200ms interval)
            let lastResult: any = null;

            intervalRef.current = setInterval(async () => {
                frameCount++;

                if (frameCount > maxFrames) {
                    // Timeout - stop verification
                    if (intervalRef.current) {
                        clearInterval(intervalRef.current);
                    }
                    handleVerificationResult(lastResult, false);
                    return;
                }

                const frameBase64 = captureFrame();
                if (frameBase64) {
                    try {
                        const result = await verificationApi.sendFrame(frameBase64);
                        console.log("Frame result:", result);

                        if (result.success && result.result) {
                            lastResult = result.result;
                            const sim = result.result.similarity;
                            if (sim !== undefined) {
                                // Convert from [-1, 1] to [0, 100]
                                const simPercent = ((sim + 1) / 2) * 100;
                                setSimilarity(Math.round(simPercent));

                                // Check if verification succeeded
                                if (result.result.same_person === true) {
                                    if (intervalRef.current) {
                                        clearInterval(intervalRef.current);
                                    }
                                    handleVerificationResult(result.result, true);
                                }
                            }
                        }
                    } catch (err) {
                        console.error("Frame error:", err);
                    }
                }
            }, 200);
        } catch (error: any) {
            console.error("Verification error:", error);
            setStatus("failed");
            setIsVerifying(false);
            alert("ການຢັ້ງຢືນລົ້ມເຫລວ: " + (error.message || "Unknown error"));
        }
    };

    const handleVerificationResult = (result: any, success: boolean) => {
        setIsVerifying(false);

        if (success && result?.same_person) {
            setStatus("success");
            setVerificationResult({
                samePerson: true,
                similarity: result.similarity,
                confidence: result.confidence,
                timestamp: new Date(),
            });

            addMessage({
                id: Math.random().toString(36).slice(2),
                role: "assistant",
                content: "ການຢັ້ງຢືນໃບໜ້າສຳເລັດ! ຕົວຕົນຂອງທ່ານໄດ້ຖືກຢືນຢັນແລ້ວ. ຂອບໃຈທີ່ໃຊ້ບໍລິການ eKYC ຂອງພວກເຮົາ.",
                timestamp: new Date(),
            });

            // Close modal after delay
            setTimeout(() => {
                closeCameraModal();
                stopCamera();
                // Reset eKYC state for next verification
                // Note: Chat history is preserved on frontend, but backend session is deleted
                setTimeout(() => {
                    resetEKYC();
                    // Keep chat history on frontend
                }, 500);
            }, 2000);
        } else {
            setStatus("failed");
            addMessage({
                id: Math.random().toString(36).slice(2),
                role: "assistant",
                content: "ການຢັ້ງຢືນໃບໜ້າລົ້ມເຫລວ. ກະລຸນາລອງໃໝ່.",
                timestamp: new Date(),
            });

            // Reset progress to id_scanned to allow retry
            setProgress("id_scanned");
        }

        // Stop WebSocket
        verificationApi.stopVerification().catch(console.error);
    };

    const handleClose = () => {
        if (intervalRef.current) {
            clearInterval(intervalRef.current);
        }
        verificationApi.stopVerification().catch(console.error);
        closeCameraModal();
        stopCamera();
        setStatus("idle");
        setSimilarity(0);
        setIsVerifying(false);
    };

    return (
        <Dialog open={cameraModalOpen} onOpenChange={handleClose}>
            <DialogContent className="sm:max-w-md">
                <DialogHeader>
                    <DialogTitle>ຢັ້ງຢືນໃບໜ້າ</DialogTitle>
                </DialogHeader>

                <div className="space-y-4">
                    <div className="relative bg-muted rounded-lg overflow-hidden aspect-video">
                        <video ref={videoRef} autoPlay playsInline muted className="w-full h-full object-cover" />
                        {status === "success" && (
                            <div className="absolute inset-0 bg-green-500/20 flex items-center justify-center">
                                <div className="bg-green-600 text-white px-4 py-2 rounded-lg flex items-center gap-2">
                                    <CheckCircle className="w-5 h-5" />
                                    ຢັ້ງຢືນສຳເລັດ
                                </div>
                            </div>
                        )}
                        {status === "failed" && (
                            <div className="absolute inset-0 bg-red-500/20 flex items-center justify-center">
                                <div className="bg-red-600 text-white px-4 py-2 rounded-lg flex items-center gap-2">
                                    <XCircle className="w-5 h-5" />
                                    ການຢັ້ງຢືນລົ້ມເຫລວ
                                </div>
                            </div>
                        )}
                    </div>

                    {similarity > 0 && <ProgressBar value={similarity} label={`ຄວາມຄ້າຍຄືກັນ: ${similarity}%`} />}

                    <div className="text-center">
                        <p className="text-sm text-muted-foreground">
                            {status === "idle"
                                ? "ວາງໃບໜ້າຂອງທ່ານໃຫ້ຢູ່ກາງກ້ອງ"
                                : status === "capturing"
                                ? "ກຳລັງຈັບພາບໃບໜ້າ..."
                                : status === "success"
                                ? "ການຢັ້ງຢືນສຳເລັດ!"
                                : "ການຢັ້ງຢືນລົ້ມເຫລວ"}
                        </p>
                    </div>

                    <div className="flex gap-2">
                        <Button variant="outline" onClick={handleClose} disabled={isVerifying} className="flex-1">
                            ຍົກເລີກ
                        </Button>
                        <Button onClick={handleStartVerification} disabled={isVerifying || status === "success"} className="flex-1 gap-2">
                            <Camera className="w-4 h-4" />
                            {isVerifying ? "ກຳລັງຢັ້ງຢືນ..." : status === "failed" ? "ລອງໃໝ່" : "ເລີ່ມຢັ້ງຢືນ"}
                        </Button>
                    </div>
                </div>
            </DialogContent>
        </Dialog>
    );
}
