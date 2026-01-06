"use client";

import { useEffect, useRef } from "react";
import { useChatStore } from "../../stores/chat-store";
import { MessageBubble } from "./message-bubble";
import { ThinkingIndicator } from "./thinking-indicator";

export function ChatBox() {
    const { messages, isLoading } = useChatStore();
    const messagesEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    return (
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-center text-muted-foreground">
                    <p className="text-xl font-semibold mb-2">ຍິນດີຕ້ອນຮັບສູ່ລະບົບ eKYC</p>
                    <p className="text-sm max-w-xs">ອັບໂຫລດບັດປະຈຳຕົວ ແລະ ຢັ້ງຢືນໃບໜ້າເພື່ອເລີ່ມຕົ້ນ</p>
                </div>
            ) : (
                <>
                    {messages.map((message) => (
                        <MessageBubble
                            key={message.id}
                            role={message.role}
                            content={message.content}
                            timestamp={message.timestamp}
                            isStreaming={message.isStreaming}
                        />
                    ))}
                    {isLoading && messages[messages.length - 1]?.role !== "assistant" && <ThinkingIndicator />}
                    <div ref={messagesEndRef} />
                </>
            )}
        </div>
    );
}
