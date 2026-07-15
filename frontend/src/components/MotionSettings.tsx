import { useEffect, useState } from "react";

import { EditLockButton } from "@/components/EditLockButton";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import { selectBusy, useSessionStore } from "@/stores/session";

interface MotionDraft {
  camera_x: number;
  camera_y: number;
  z_approach: number;
  z_measure: number;
  travel_speed: number;
  known_jog_mm: number;
}

const FIELDS: { key: keyof MotionDraft; label: string; step?: string; unit: string }[] = [
  { key: "known_jog_mm", label: "Cal jog", step: "0.1", unit: "mm" },
  { key: "camera_x", label: "Camera X", step: "0.1", unit: "mm" },
  { key: "camera_y", label: "Camera Y", step: "0.1", unit: "mm" },
  { key: "z_approach", label: "Z approach", step: "0.1", unit: "mm" },
  { key: "z_measure", label: "Z measure", step: "0.1", unit: "mm" },
  { key: "travel_speed", label: "Move speed", step: "1", unit: "mm / min"},
];

function draftFromStatus(status: {
  camera_x: number;
  camera_y: number;
  z_approach: number;
  z_measure: number;
  travel_speed: number;
  known_jog_mm: number;
}): MotionDraft {
  return {
    camera_x: status.camera_x,
    camera_y: status.camera_y,
    z_approach: status.z_approach,
    z_measure: status.z_measure,
    travel_speed: status.travel_speed,
    known_jog_mm: status.known_jog_mm,
  };
}

export function MotionSettings() {
  const status = useSessionStore((s) => s.status);
  const busy = useSessionStore(selectBusy);
  const updatePrefs = useSessionStore((s) => s.updatePrefs);

  const [locked, setLocked] = useState(true);
  const [draft, setDraft] = useState<MotionDraft | null>(null);
  const [dirty, setDirty] = useState(false);

  useEffect(() => {
    if (!status || dirty) return;
    setDraft(draftFromStatus(status));
  }, [
    status,
    dirty,
    status?.camera_x,
    status?.camera_y,
    status?.z_approach,
    status?.z_measure,
    status?.travel_speed,
    status?.known_jog_mm,
  ]);

  if (!status || !draft) return null;

  const save = () => {
    if (!draft || !dirty) return;
    setDirty(false);
    void updatePrefs(draft);
  };

  const toggleLock = () => {
    setLocked((prev) => {
      if (!prev) {
        if (dirty) save();
        else setDraft(draftFromStatus(status));
      }
      return !prev;
    });
  };

  const setField = (key: keyof MotionDraft, raw: string) => {
    const value = key === "travel_speed" ? parseInt(raw, 10) : parseFloat(raw);
    if (Number.isNaN(value)) return;
    setDraft((d) => (d ? { ...d, [key]: value } : d));
    setDirty(true);
  };

  return (
    <Card className="relative">
      <EditLockButton locked={locked} label="motion settings" onToggle={toggleLock} />
      <CardHeader className="pb-2 pr-9">
        <CardTitle className="text-base">Motion</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
          {FIELDS.map(({ key, label, step, unit }) => {
            const inputPad = key === "travel_speed" ? "pr-14" : "pr-9";
            return (
            <label key={key} className="space-y-1 text-xs">
              <span className="text-muted-foreground">{label}</span>
              <div className="relative">
                {locked ? (
                  <Input
                    readOnly
                    tabIndex={-1}
                    className={cn(
                      "cursor-default border-transparent bg-transparent tabular-nums shadow-none focus-visible:ring-0",
                      inputPad,
                    )}
                    value={String(draft[key])}
                  />
                ) : (
                  <Input
                    type="number"
                    step={step}
                    disabled={busy}
                    className={cn("tabular-nums", inputPad)}
                    value={draft[key]}
                    onChange={(e) => setField(key, e.target.value)}
                    onBlur={save}
                  />
                )}
                <span className="pointer-events-none absolute inset-y-0 right-2.5 flex items-center text-[10px] text-muted-foreground max-w-8 break-words">
                  {unit}
                </span>
              </div>
            </label>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
