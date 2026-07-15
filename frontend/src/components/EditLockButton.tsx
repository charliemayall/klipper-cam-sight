import { Lock, LockOpen } from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface EditLockButtonProps {
  locked: boolean;
  label: string;
  onToggle: () => void;
}

/** Place inside a `relative` card; renders a top-right quarter-circle wedge. */
export function EditLockButton({ locked, label, onToggle }: EditLockButtonProps) {
  const icon = locked ? <Lock className="size-3.5" /> : <LockOpen className="size-3.5" />;

  return (
    <div className="pointer-events-none absolute top-0 right-0 z-10 size-10 overflow-hidden rounded-tr-xl">
      <div
        aria-hidden
        className="absolute top-0 right-0 size-20 rounded-full bg-secondary ring-1 ring-foreground/10 translate-x-1/2 -translate-y-1/2"
      />
      <Button
        size="icon-xs"
        variant="ghost"
        className={cn("pointer-events-auto absolute right-1.5 top-1.5 text-muted-foreground hover:bg-foreground/5", 
          !locked && "text-primary hover:text-primary")}
        aria-label={locked ? `Unlock ${label}` : `Lock ${label}`}
        aria-pressed={!locked}
        onClick={onToggle}
      >
        {icon}
      </Button>
    </div>
  );
}
