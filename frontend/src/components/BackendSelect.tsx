import { Info } from "lucide-react";

import { BackendType } from "@/api";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  HoverCard,
  HoverCardContent,
  HoverCardTrigger,
} from "@/components/ui/hover-card";
import { BACKEND_INFO, BACKEND_OPTIONS, backendLabel } from "@/lib/backends";
import { cn } from "@/lib/utils";
import { selectBusy, useSessionStore } from "@/stores/session";
import { buttonVariants } from "./ui/button";

function BackendInfoButton({ type }: { type: BackendType }) {
  const info = BACKEND_INFO[type];

  return (
    <HoverCard>
      <HoverCardTrigger
        render={
          <button
            type="button"
            aria-label={`About ${info.label} backend`}
            className="inline-flex size-6 shrink-0 items-center justify-center rounded-md text-muted-foreground hover:bg-muted hover:text-foreground"
            onPointerDown={(e) => e.stopPropagation()}
            onClick={(e) => e.stopPropagation()}
          >
            <Info className="size-3.5" />
          </button>
        }
      />
      <HoverCardContent side="right" align="start" className="w-72 space-y-2">
        <p className="font-medium leading-snug">{info.title}</p>
        <p className="text-xs leading-relaxed text-muted-foreground">
          {info.summary}
        </p>
        <ul className="list-disc space-y-1 pl-4 text-xs text-muted-foreground">
          {info.bullets.map((line) => (
            <li key={line}>{line}</li>
          ))}
        </ul>
      </HoverCardContent>
    </HoverCard>
  );
}

export function BackendSelect() {
  const status = useSessionStore((s) => s.status);
  const busy = useSessionStore(selectBusy);
  const setBackend = useSessionStore((s) => s.setBackend);

  if (!status) return null;

  return (
    <div className="space-y-1.5">
      <div className="flex items-center gap-0.5">
        <Select
          value={status.backend}
          disabled={busy}
          onValueChange={(value) =>
            value && void setBackend(value as BackendType)
          }
        >
          <SelectTrigger
            size="sm"
            className={cn(
              buttonVariants({ variant: "ghost", size: "sm" }),
              "min-w-16 w-fit justify-between border-transparent bg-transparent text-muted-foreground shadow-none hover:text-foreground dark:bg-transparent",
            )}
          >
            <SelectValue placeholder="Backend" />
          </SelectTrigger>
          <SelectContent>
            {BACKEND_OPTIONS.map((type) => (
              <SelectItem key={type} value={type}>
                <span className="flex w-full items-center justify-between gap-2">
                  <span>{backendLabel(type)} </span>
                  <BackendInfoButton type={type} />
                </span>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
    </div>
  );
}
