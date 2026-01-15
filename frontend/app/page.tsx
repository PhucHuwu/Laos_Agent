"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { ChatContainer } from "./ekyc/components/layout/chat-container";
import { UploadModal } from "./ekyc/components/modals/upload-modal";
import { CameraModal } from "./ekyc/components/modals/camera-modal";
import { useAuthStore } from "./ekyc/stores/auth-store";

export default function Home() {
    const router = useRouter();
    const { isAuthenticated, checkAuth, logout, user } = useAuthStore();

    useEffect(() => {
        checkAuth();
    }, [checkAuth]);

    useEffect(() => {
        if (!isAuthenticated) {
            router.push("/login");
        }
    }, [isAuthenticated, router]);

    const handleLogout = () => {
        logout();
        router.push("/login");
    };

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
