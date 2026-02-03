"use client";

import { useEffect, useCallback, useRef } from "react";
import { ChatBox } from "../chat/chat-box";
import { ChatInput } from "../chat/chat-input";
import { QuickActions } from "../chat/quick-actions";
import { Header } from "./header";
import { UserInfoSidebar } from "./user-info-sidebar";
import { useChatStore } from "../../stores/chat-store";
import { useUIStore } from "../../stores/ui-store";
import { useEKYCStore } from "../../stores/ekyc-store";
import { chatApi } from "../../api/chat";

export function ChatContainer() {
    const { messages, addMessage, updateLastMessage, setLoading, isLoading, loadHistory } = useChatStore();
    const { openUploadModal, openCameraModal, toggleSidebar } = useUIStore();
    const { progress, idCardUrl } = useEKYCStore();

    // Swipe gesture handling
    const touchStartX = useRef<number>(0);
    const touchEndX = useRef<number>(0);

    const handleTouchStart = (e: React.TouchEvent) => {
        touchStartX.current = e.touches[0].clientX;
    };

    const handleTouchMove = (e: React.TouchEvent) => {
        touchEndX.current = e.touches[0].clientX;
    };

    const handleTouchEnd = () => {
        const swipeDistance = touchEndX.current - touchStartX.current;
        // Swipe right from left edge (within 50px of left edge) to open sidebar
        if (touchStartX.current < 50 && swipeDistance > 80) {
            toggleSidebar();
        }
        touchStartX.current = 0;
        touchEndX.current = 0;
    };

    // Load history on mount
    useEffect(() => {
        loadHistory();
    }, [loadHistory]);

    // Add welcome message if no messages (and history loaded)
    useEffect(() => {
        if (messages.length === 0 && !isLoading) {
            const timer = setTimeout(() => {
                if (messages.length === 0) {
                    addMessage({
                        id: "welcome",
                        role: "assistant",
                        content:
                            "ສະບາຍດີ! ຍິນດີຕ້ອນຮັບສູ່ລະບົບ eKYC ລາວ. ຂ້ອຍແມ່ນຜູ້ຊ່ວຍ AI ທີ່ຈະຊ່ວຍທ່ານຢັ້ງຢືນຕົວຕົນ. ທ່ານສາມາດເລີ່ມຕົ້ນໂດຍການຖາມຄຳຖາມ ຫຼື ກົດປຸ່ມດ້ານລຸ່ມເພື່ອເລີ່ມຕົ້ນ.",
                        timestamp: new Date(),
                    });
                }
            }, 500);
            return () => clearTimeout(timer);
        }
    }, [messages.length, addMessage, isLoading]);

    const handleToolCalls = useCallback(
        (toolCalls: any[]) => {
            for (const toolCall of toolCalls) {
                const functionName = toolCall?.function?.name;

                // Parse message from tool call arguments
                try {
                    const args = JSON.parse(toolCall.function?.arguments || "{}");
                    if (args.message) {
                        addMessage({
                            id: Math.random().toString(36).slice(2),
                            role: "assistant",
                            content: args.message,
                            timestamp: new Date(),
                        });
                    }
                } catch (e) {
                    console.error("Error parsing tool call arguments:", e);
                }

                // Execute tool action based on function name
                setTimeout(() => {
                    if (functionName === "open_id_scan") {
                        openUploadModal();
                    } else if (functionName === "open_face_verification") {
                        openCameraModal();
                    }
                }, 500);
            }
        },
        [addMessage, openUploadModal, openCameraModal],
    );

    const handleSendMessage = async (message: string) => {
        if (isLoading) return;

        // Add user message
        addMessage({
            id: Math.random().toString(36).slice(2),
            role: "user",
            content: message,
            timestamp: new Date(),
        });

        setLoading(true);

        try {
            // Use streaming API
            let fullContent = "";
            let hasToolCalls = false;
            let toolCalls: any[] = [];
            // ... (rest is same)

            // Add placeholder for assistant message
            const assistantMsgId = Math.random().toString(36).slice(2);
            addMessage({
                id: assistantMsgId,
                role: "assistant",
                content: "",
                timestamp: new Date(),
                isStreaming: true,
            });

            for await (const chunk of chatApi.streamChat(message)) {
                if (chunk.type === "content") {
                    fullContent = chunk.full_content || fullContent + (chunk.content || "");
                    updateLastMessage(fullContent);
                } else if (chunk.type === "tool_calls") {
                    hasToolCalls = true;
                    toolCalls = chunk.tool_calls || [];
                } else if (chunk.type === "done") {
                    if (chunk.tool_calls) {
                        hasToolCalls = true;
                        toolCalls = chunk.tool_calls;
                    }
                    // Finalize message
                    updateLastMessage(fullContent || chunk.content || "", false);
                } else if (chunk.type === "error") {
                    updateLastMessage("ຂໍອະໄພ, ເກີດຂໍ້ຜິດພາດ: " + chunk.error, false);
                }
            }

            // Handle tool calls after streaming
            if (hasToolCalls && toolCalls.length > 0) {
                handleToolCalls(toolCalls);
            }
        } catch (error: any) {
            console.error("Chat error:", error);
            addMessage({
                id: Math.random().toString(36).slice(2),
                role: "assistant",
                content: "ຂໍອະໄພ, ເກີດຂໍ້ຜິດພາດໃນການເຊື່ອມຕໍ່. ກະລຸນາລອງໃໝ່.",
                timestamp: new Date(),
            });
        } finally {
            setLoading(false);
        }
    };

    const handleQuickAction = (action: string) => {
        switch (action) {
            case "upload_id":
                openUploadModal();
                break;
            case "start_verification":
                handleSendMessage("ຂ້ອຍຕ້ອງການເລີ່ມຕົ້ນຂະບວນການ eKYC");
                break;
            case "help":
                handleSendMessage("ຂ້ອຍຕ້ອງການຄວາມຊ່ວຍເຫຼືອກ່ຽວກັບຂະບວນການ eKYC");
                break;
        }
    };

    return (
        <div
            className="flex flex-col h-screen bg-background overflow-hidden"
            onTouchStart={handleTouchStart}
            onTouchMove={handleTouchMove}
            onTouchEnd={handleTouchEnd}
        >
            <Header />
            <div className="flex-1 flex overflow-hidden">
                {/* Sidebar */}
                <UserInfoSidebar />

                {/* Main Chat Area */}
                <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
                    <div className="flex-1 flex flex-col max-w-3xl mx-auto w-full px-4 min-h-0 overflow-hidden">
                        <ChatBox />
                        {messages.length <= 1 && <QuickActions onAction={handleQuickAction} isLoading={isLoading} />}
                    </div>
                    <div className="max-w-3xl mx-auto w-full px-4">
                        <ChatInput onSend={handleSendMessage} isLoading={isLoading} />
                    </div>
                </div>
            </div>
        </div>
    );
}
