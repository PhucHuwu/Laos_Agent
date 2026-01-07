"use client";

import type React from "react";

import { useState, useRef } from "react";
import { Upload, X } from "lucide-react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { ProgressBar } from "../ui/progress-bar";
import { useUIStore } from "../../stores/ui-store";
import { useEKYCStore } from "../../stores/ekyc-store";
import { uploadApi } from "../../api/upload";
import { useChatStore } from "../../stores/chat-store";

export function UploadModal() {
    const { uploadModalOpen, closeUploadModal, openCameraModal } = useUIStore();
    const { setIdCardUrl, setScanResult, setProgress: setEKYCProgress } = useEKYCStore();
    const { addMessage } = useChatStore();

    const [isDragging, setIsDragging] = useState(false);
    const [isUploading, setIsUploading] = useState(false);
    const [uploadProgress, setUploadProgress] = useState(0);
    const [preview, setPreview] = useState<string | null>(null);
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = () => {
        setIsDragging(false);
    };

    const handleDrop = async (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelect(files[0]);
        }
    };

    const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);
        }
    };

    const handleFileSelect = (file: File) => {
        // Validate file type
        if (!file.type.startsWith("image/")) {
            alert("ກະລຸນາອັບໂຫລດໄຟລ໌ຮູບພາບ");
            return;
        }

        setSelectedFile(file);

        // Show preview
        const reader = new FileReader();
        reader.onload = (e) => {
            setPreview(e.target?.result as string);
        };
        reader.readAsDataURL(file);
    };

    const handleUpload = async () => {
        if (!selectedFile) return;

        setIsUploading(true);
        setUploadProgress(0);

        try {
            const response = await uploadApi.uploadIdCard(selectedFile, (p) => setUploadProgress(p));

            console.log("Upload response:", response);

            // Backend returns flat response, not wrapped in data
            if (response.success) {
                const imageUrl = response.image_url || response.id_card_url;
                setIdCardUrl(imageUrl || "");
                setScanResult(response.scan_result);
                setEKYCProgress("id_scanned");

                // Format fields for display
                const fields = response.scan_result?.fields;
                let infoText = "ອັບໂຫລດບັດປະຈຳຕົວສຳເລັດ!";
                if (fields) {
                    infoText += `\n\n**ຂໍ້ມູນທີ່ສະກັດໄດ້:**\n\n`;

                    // Personal information
                    if (fields.id_number) infoText += `- **ເລກບັດ:** ${fields.id_number}\n`;
                    if (fields.fullname) infoText += `- **ຊື່ເຕັມ:** ${fields.fullname}\n`;
                    if (fields.dob) infoText += `- **ວັນເດືອນປີເກີດ:** ${fields.dob}\n`;
                    if (fields.nationality) infoText += `- **ສັນຊາດ:** ${fields.nationality}\n`;
                    if (fields.ethnicity) infoText += `- **ເຊື້ອຊາດ:** ${fields.ethnicity}\n`;

                    // Address information
                    const address = fields.address;
                    if (address) {
                        infoText += `\n**ທີ່ຢູ່:**\n`;
                        if (address.address) {
                            infoText += `${address.address}\n`;
                        }
                        const children = address.childrent;
                        if (children) {
                            if (children.address_village) infoText += `- ບ້ານ: ${children.address_village}\n`;
                            if (children.address_district) infoText += `- ເມືອງ: ${children.address_district}\n`;
                            if (children.address_province) infoText += `- ແຂວງ: ${children.address_province}\n`;
                        }
                    }

                    // Date information
                    if (fields.issue_date || fields.expiry_date) {
                        infoText += `\n**ວັນທີອອກ/ໝົດອາຍຸ:**\n`;
                        if (fields.issue_date) infoText += `- ອອກໃຫ້: ${fields.issue_date}\n`;
                        if (fields.expiry_date) infoText += `- ໝົດອາຍຸ: ${fields.expiry_date}\n`;
                    }
                }

                // Add message to chat
                addMessage({
                    id: Math.random().toString(36).slice(2),
                    role: "assistant",
                    content: infoText,
                    timestamp: new Date(),
                });

                // Close modal and handle tool_call if present
                setTimeout(() => {
                    closeUploadModal();
                    setPreview(null);
                    setSelectedFile(null);
                    setUploadProgress(0);

                    // Handle tool_call from backend
                    if (response.tool_call && response.tool_call.auto_execute) {
                        const toolName = response.tool_call.function?.name;

                        // Parse message from tool call
                        try {
                            const args = JSON.parse(response.tool_call.function?.arguments || "{}");
                            if (args.message) {
                                addMessage({
                                    id: Math.random().toString(36).slice(2),
                                    role: "assistant",
                                    content: args.message,
                                    timestamp: new Date(),
                                });
                            }
                        } catch (e) {
                            console.error("Error parsing tool_call arguments:", e);
                        }

                        // Execute tool action
                        if (toolName === "open_face_verification") {
                            openCameraModal();
                        }
                    }
                }, 1000);
            } else {
                alert(response.error || "ການອັບໂຫລດລົ້ມເຫລວ");
            }
        } catch (error: any) {
            console.error("Upload error:", error);
            alert("ການອັບໂຫລດລົ້ມເຫລວ: " + (error.message || "Unknown error"));
        } finally {
            setIsUploading(false);
        }
    };

    const handleClose = () => {
        closeUploadModal();
        setPreview(null);
        setSelectedFile(null);
        setUploadProgress(0);
    };

    return (
        <Dialog open={uploadModalOpen} onOpenChange={handleClose}>
            <DialogContent className="sm:max-w-md">
                <DialogHeader>
                    <DialogTitle>ອັບໂຫລດບັດປະຈຳຕົວ</DialogTitle>
                </DialogHeader>

                <div className="space-y-4">
                    {preview ? (
                        <div className="relative">
                            <img src={preview} alt="ID card preview" className="w-full rounded-lg" />
                            <button
                                onClick={() => {
                                    setPreview(null);
                                    setSelectedFile(null);
                                }}
                                className="absolute top-2 right-2 p-1 bg-destructive text-destructive-foreground rounded-lg"
                            >
                                <X className="w-4 h-4" />
                            </button>
                        </div>
                    ) : (
                        <div
                            onDragOver={handleDragOver}
                            onDragLeave={handleDragLeave}
                            onDrop={handleDrop}
                            onClick={() => fileInputRef.current?.click()}
                            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                                isDragging ? "border-primary bg-primary/5" : "border-border hover:border-primary/50"
                            }`}
                        >
                            <Upload className="w-8 h-8 mx-auto mb-2 text-muted-foreground" />
                            <p className="font-medium mb-1">ລາກແລ້ວວາງບັດປະຈຳຕົວຂອງທ່ານທີ່ນີ້</p>
                            <p className="text-sm text-muted-foreground">ຫຼືຄລິກເພື່ອເລືອກໄຟລ໌</p>
                        </div>
                    )}

                    <input ref={fileInputRef} type="file" accept="image/*" onChange={handleFileInput} className="hidden" disabled={isUploading} />

                    {isUploading && <ProgressBar value={uploadProgress} label="ກຳລັງອັບໂຫລດ..." />}

                    <div className="flex gap-2">
                        <Button variant="outline" onClick={handleClose} disabled={isUploading} className="flex-1">
                            ຍົກເລີກ
                        </Button>
                        <Button onClick={handleUpload} disabled={!selectedFile || isUploading} className="flex-1">
                            {isUploading ? "ກຳລັງອັບໂຫລດ..." : "ອັບໂຫລດ"}
                        </Button>
                    </div>
                </div>
            </DialogContent>
        </Dialog>
    );
}
