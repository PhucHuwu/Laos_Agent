import { create } from "zustand";
import type { Message } from "../types/chat";

interface ChatState {
    messages: Message[];
    isLoading: boolean;
    sessionId: string;

    addMessage: (msg: Message) => void;
    updateLastMessage: (content: string, isStreaming?: boolean) => void;
    setLoading: (loading: boolean) => void;
    setSessionId: (id: string) => void;
    reset: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
    messages: [],
    isLoading: false,
    sessionId: "",

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
    setSessionId: (id) => set({ sessionId: id }),
    reset: () => set({ messages: [], isLoading: false }),
}));
