import { Markdown } from "./markdown";

interface MessageBubbleProps {
    role: "user" | "assistant" | "system";
    content: string;
    timestamp?: Date;
    isStreaming?: boolean;
}

export function MessageBubble({ role, content, timestamp, isStreaming }: MessageBubbleProps) {
    const isUser = role === "user";

    return (
        <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
            <div
                className={`max-w-xs lg:max-w-md px-4 py-3 rounded-lg ${
                    isUser ? "bg-primary text-primary-foreground rounded-br-none" : "bg-muted text-muted-foreground dark:text-white rounded-bl-none"
                }`}
            >
                <div className="text-sm">
                    {role === "assistant" ? (
                        <>
                            <Markdown content={content} />
                            {isStreaming && <span className="inline-block w-2 h-4 ml-1 bg-current animate-pulse" />}
                        </>
                    ) : (
                        <p>{content}</p>
                    )}
                </div>
                {timestamp && !isStreaming && <p className="text-xs mt-2 opacity-70">{timestamp.toLocaleTimeString()}</p>}
            </div>
        </div>
    );
}
