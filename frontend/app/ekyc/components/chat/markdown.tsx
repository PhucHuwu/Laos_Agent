import ReactMarkdown from "react-markdown"

interface MarkdownProps {
  content: string
}

export function Markdown({ content }: MarkdownProps) {
  return (
    <ReactMarkdown
      components={{
        p: ({ node, ...props }) => <p className="mb-2" {...props} />,
        strong: ({ node, ...props }) => <strong className="font-semibold" {...props} />,
        em: ({ node, ...props }) => <em className="italic" {...props} />,
        ul: ({ node, ...props }) => <ul className="list-disc list-inside mb-2" {...props} />,
        ol: ({ node, ...props }) => <ol className="list-decimal list-inside mb-2" {...props} />,
        li: ({ node, ...props }) => <li className="mb-1" {...props} />,
        code: ({ node, inline, ...props }: any) =>
          inline ? (
            <code className="bg-muted px-1 rounded text-xs" {...props} />
          ) : (
            <pre className="bg-muted p-2 rounded mb-2 overflow-auto">
              <code {...props} />
            </pre>
          ),
      }}
    >
      {content}
    </ReactMarkdown>
  )
}
