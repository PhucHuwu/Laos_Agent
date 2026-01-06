export interface Message {
    id: string;
    role: "user" | "assistant" | "system";
    content: string;
    timestamp: Date;
    toolCalls?: ToolCall[];
    isStreaming?: boolean;
}

export interface ToolCall {
    id: string;
    name: string;
    arguments: Record<string, any>;
}

export interface StreamChunk {
    type: "thinking" | "content" | "tool_calls" | "done" | "error";
    content?: string;
    fullContent?: string;
    toolCalls?: ToolCall[];
    error?: string;
}

export interface Conversation {
    id: string;
    messages: Message[];
    createdAt: Date;
    updatedAt: Date;
}
