"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { ChatContainer } from "./ekyc/components/layout/chat-container";
import { UploadModal } from "./ekyc/components/modals/upload-modal";
import { CameraModal } from "./ekyc/components/modals/camera-modal";
import { useAuthStore } from "./ekyc/stores/auth-store";

export default function Home() {
    const router = useRouter();
    const { isAuthenticated, isInitialized, checkAuth } = useAuthStore();

    useEffect(() => {
        checkAuth();
    }, [checkAuth]);

    useEffect(() => {
        // Only redirect after auth check is complete
        if (isInitialized && !isAuthenticated) {
            router.push("/login");
        }
    }, [isAuthenticated, isInitialized, router]);

    // Show loading while checking auth
    if (!isInitialized) {
        return (
            <div className="h-screen flex items-center justify-center bg-background">
                <div className="text-muted-foreground">Đang tải...</div>
            </div>
        );
    }

    if (!isAuthenticated) {
        return (
            <div className="h-screen flex items-center justify-center bg-background">
                <div className="text-muted-foreground">Đang chuyển hướng...</div>
            </div>
        );
    }

    return (
        <div className="h-screen flex flex-col bg-background">
            <ChatContainer />
            <UploadModal />
            <CameraModal />
        </div>
    );
}
