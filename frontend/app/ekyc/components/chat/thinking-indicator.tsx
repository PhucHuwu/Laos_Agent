import { Spinner } from "../ui/spinner"

export function ThinkingIndicator() {
  return (
    <div className="flex items-center gap-2 text-muted-foreground">
      <Spinner />
      <span className="text-sm">Thinking...</span>
    </div>
  )
}
