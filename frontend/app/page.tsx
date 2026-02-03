"use client";

import { ChatContainer } from "./ekyc/components/layout/chat-container";
import { UploadModal } from "./ekyc/components/modals/upload-modal";
import { CameraModal } from "./ekyc/components/modals/camera-modal";

export default function Home() {
    return (
        <div className="h-screen flex flex-col bg-background">
            <ChatContainer />
            <UploadModal />
            <CameraModal />
        </div>
    );
}
