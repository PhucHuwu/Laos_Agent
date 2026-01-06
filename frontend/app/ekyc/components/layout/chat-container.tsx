"use client";

import { useEffect, useCallback } from "react";
import { ChatBox } from "../chat/chat-box";
import { ChatInput } from "../chat/chat-input";
import { QuickActions } from "../chat/quick-actions";
import { Header } from "./header";
import { useChatStore } from "../../stores/chat-store";
import { useUIStore } from "../../stores/ui-store";
import { useEKYCStore } from "../../stores/ekyc-store";
import { chatApi } from "../../api/chat";

export function ChatContainer() {
    const { messages, addMessage, updateLastMessage, setLoading, isLoading, sessionId, setSessionId } = useChatStore();
    const { openUploadModal, openCameraModal } = useUIStore();
    const { progress, idCardUrl } = useEKYCStore();

    // Initialize session on mount
    useEffect(() => {
        let id = localStorage.getItem("sessionId");
        if (!id) {
            id = "session-" + Date.now() + "-" + Math.random().toString(36).slice(2);
            localStorage.setItem("sessionId", id);
        }
        setSessionId(id);
    }, [setSessionId]);

    // Add welcome message on first load
    useEffect(() => {
        if (messages.length === 0 && sessionId) {
            addMessage({
                id: "welcome",
                role: "assistant",
                content:
                    "ສະບາຍດີ! ຍິນດີຕ້ອນຮັບສູ່ລະບົບ eKYC ລາວ. ຂ້ອຍແມ່ນຜູ້ຊ່ວຍ AI ທີ່ຈະຊ່ວຍທ່ານຢັ້ງຢືນຕົວຕົນ. ທ່ານສາມາດເລີ່ມຕົ້ນໂດຍການຖາມຄຳຖາມ ຫຼື ກົດປຸ່ມດ້ານລຸ່ມເພື່ອເລີ່ມຕົ້ນ.",
                timestamp: new Date(),
            });
        }
    }, [messages.length, sessionId, addMessage]);

    const handleToolCalls = useCallback(
        (toolCalls: any[]) => {
            for (const toolCall of toolCalls) {
                const functionName = toolCall?.function?.name;
                if (functionName === "start_ekyc_process") {
                    try {
                        const args = JSON.parse(toolCall.function.arguments || "{}");
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

                    // Check current progress to decide which modal to open
                    setTimeout(() => {
                        if (progress === "id_scanned" && idCardUrl) {
                            // ID already scanned, open camera for face verification
                            openCameraModal();
                        } else {
                            // Need to upload/scan ID first
                            openUploadModal();
                        }
                    }, 500);
                }
            }
        },
        [addMessage, openUploadModal, openCameraModal, progress, idCardUrl]
    );

    const handleSendMessage = async (message: string) => {
        if (!sessionId || isLoading) return;

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
        <div className="flex flex-col h-screen bg-background">
            <Header />
            <div className="flex-1 flex flex-col max-w-3xl mx-auto w-full px-4">
                <ChatBox />
                {messages.length <= 1 && <QuickActions onAction={handleQuickAction} isLoading={isLoading} />}
            </div>
            <div className="max-w-3xl mx-auto w-full px-4">
                <ChatInput onSend={handleSendMessage} isLoading={isLoading} />
            </div>
        </div>
    );
}
