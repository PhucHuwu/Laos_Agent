import { create } from "zustand";
import type { Message } from "../types/chat";
import { chatApi } from "../api/chat";

interface ChatState {
    messages: Message[];
    isLoading: boolean;

    addMessage: (msg: Message) => void;
    updateLastMessage: (content: string, isStreaming?: boolean) => void;
    setLoading: (loading: boolean) => void;
    reset: () => void;
    loadHistory: () => Promise<void>;
}

export const useChatStore = create<ChatState>((set) => ({
    messages: [],
    isLoading: false,

    addMessage: (msg) =>
        set((state) => ({
            messages: [...state.messages, msg],
        })),

    updateLastMessage: (content, isStreaming = true) =>
        set((state) => {
            const messages = [...state.messages];
            if (messages.length > 0) {
                messages[messages.length - 1] = {
                    ...messages[messages.length - 1],
                    content,
                    isStreaming,
                };
            }
            return { messages };
        }),

    setLoading: (loading) => set({ isLoading: loading }),
    reset: () => set({ messages: [], isLoading: false }),

    loadHistory: async () => {
        try {
            set({ isLoading: true });
            const response = await chatApi.getHistory();
            if (response.success && response.messages) {
                const mappedMessages = response.messages.map((msg: any) => {
                    let content = msg.content;

                    // Extract content from tool call if content is empty (common pattern for tool-generated responses)
                    if ((!content || !content.trim()) && msg.tool_calls && Array.isArray(msg.tool_calls)) {
                        for (const toolCall of msg.tool_calls) {
                            if (toolCall.function?.arguments) {
                                try {
                                    const args = JSON.parse(toolCall.function.arguments);
                                    if (args.message) {
                                        content = args.message;
                                        break;
                                    }
                                } catch (e) {
                                    // Ignore parsing errors
                                }
                            }
                        }
                    }

                    return {
                        id: "msg-" + Date.now() + "-" + Math.random().toString(36).slice(2),
                        role: msg.role,
                        content: content,
                        timestamp: new Date(msg.timestamp),
                        isStreaming: false,
                    };
                });
                set({ messages: mappedMessages });

                // Sync progress if available
                if (response.progress) {
                    // Import dynamically to avoid circular dependency if possible, or use window/event
                    // But simpler: access store directly if imports allow.
                    // Circular dev dependency might be an issue if stores import each other.
                    // Let's use the global store access pattern if possible, or just ignore for now to avoid complexity?
                    // No, user wants persistence.
                    // Assuming we can import useEKYCStore here.
                    const { useEKYCStore } = require("./ekyc-store");
                    useEKYCStore.getState().setProgress(response.progress);
                    if (response.context?.id_card_url) {
                        useEKYCStore.getState().setIdCardUrl(response.context.id_card_url);
                    }
                }
            }
        } catch (error) {
            console.error("Failed to load chat history:", error);
        } finally {
            set({ isLoading: false });
        }
    },
}));
