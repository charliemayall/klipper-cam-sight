import { useCallback, useEffect, useRef } from "react";
import { AnimatePresence, motion, useReducedMotion } from "motion/react";
import { toast } from "sonner";

import { camSight } from "@/lib/camSightClient";
import { cameraCardFooter } from "@/lib/cameraFooter";
import { ActionBar } from "@/components/ActionBar";
import { CameraPanel, type CameraPanelHandle } from "@/components/CameraPanel";
import { Help } from "@/components/Help";
import { MacrosPanel } from "@/components/MacrosPanel";
import { MotionSettings } from "@/components/MotionSettings";
import { OffsetsPanel } from "@/components/OffsetsPanel";
import { BackendSelect } from "@/components/BackendSelect";
import { ThemePicker } from "@/components/ThemePicker";
import { WebcamSelect } from "@/components/WebcamSelect";
import { instructions, WizardNav } from "@/components/WizardNav";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Toaster } from "@/components/ui/sonner";
import {
  disposeSessionGhost,
  selectBusy,
  useSessionStore,
} from "@/stores/session";
import {
  useOffsetsDirtyGuard,
  useSessionPolling,
} from "@/stores/useSessionEffects";

function isTypingTarget(target: EventTarget | null) {
  const el = target as HTMLElement | null;
  if (!el) return false;
  const tag = el.tagName;
  return (
    tag === "INPUT" ||
    tag === "TEXTAREA" ||
    tag === "SELECT" ||
    el.isContentEditable
  );
}

export default function App() {
  const status = useSessionStore((s) => s.status);
  const error = useSessionStore((s) => s.error);
  const tool0GhostSrc = useSessionStore((s) => s.tool0GhostSrc);
  const busy = useSessionStore(selectBusy);
  const cameraClick = useSessionStore((s) => s.cameraClick);
  const undo = useSessionStore((s) => s.undo);
  const hardReset = useSessionStore((s) => s.hardReset);

  const cameraRef = useRef<CameraPanelHandle>(null);
  const reduceMotion = useReducedMotion();
  const fade = reduceMotion ? { duration: 0 } : { duration: 0.15 };

  useSessionPolling();
  useOffsetsDirtyGuard();

  useEffect(() => () => disposeSessionGhost(), []);

  const handleUndo = useCallback(() => {
    void undo(() => cameraRef.current?.undoLocalPick() ?? false);
  }, [undo]);

  const triggerEstop = useCallback(() => {
    void camSight
      .emergencyStop()
      .then(() => toast.success("E-stop sent"))
      .catch(() => toast.error("E-stop failed"));
  }, []);

  const lastSpaceTapRef = useRef(0);

  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "z" && !e.shiftKey) {
        if (isTypingTarget(e.target)) return;
        e.preventDefault();
        handleUndo();
        return;
      }
      if (e.key !== " " && e.code !== "Space") return;
      if (e.repeat || e.metaKey || e.ctrlKey || e.altKey) return;
      if (isTypingTarget(e.target)) return;

      const now = Date.now();
      if (now - lastSpaceTapRef.current < 1000) {
        e.preventDefault();
        lastSpaceTapRef.current = 0;
        triggerEstop();
      } else {
        lastSpaceTapRef.current = now;
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [handleUndo, triggerEstop]);

  const cameraFooter = status ? cameraCardFooter(status) : null;

  return (
    <div className="flex min-h-screen flex-col bg-background transition-colors duration-300 ease-in-out">
      <Toaster richColors position="top-right" />
      <header className="app-header grid grid-cols-[1fr_auto_1fr] items-center gap-3 border-b px-4 py-3">
        <div className="flex items-center gap-3 justify-self-start">
          <h1 className="text-lg font-semibold">
            <span className="logo-word">Cam</span>
            <span className="logo-second">Sight</span>
          </h1>
          {status && <WebcamSelect />}
        </div>
        <Button
          variant="destructive"
          size="lg"
          className="min-w-72 flex-row justify-between gap-0.5 justify-self-center border-destructive font-bold tracking-wider text-destructive-foreground hover:bg-destructive/90 hover:text-white"
          onClick={triggerEstop}
        >
          <span className="font-mono text-destructive">E-STOP</span>

          <kbd className="rounded-xs bg-muted px-1.5 py-0.5 text-xs font-medium text-muted-foreground">
            Space x2
          </kbd>
        </Button>
        <div className="justify-self-end">
          <ThemePicker />
        </div>
      </header>

      {error && (
        <Alert variant="destructive" className="m-4">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <main className="grid flex-1 gap-4 p-4 lg:grid-cols-[240px_1fr_280px]">
        <Card className="h-full">
          <CardHeader>
            <CardTitle className="text-base">Wizard</CardTitle>
          </CardHeader>
          <Separator />
          <CardContent className="space-y-4 h-full">
            {status && (
              <>
                <WizardNav />
                <Separator />
                <AnimatePresence mode="wait">
                  <motion.div
                    key={`${status.wizard_step}-${status.calibration_clicks}`}
                    initial={{ opacity: 0, y: 4 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -4 }}
                    transition={fade}
                  >
                    <CardDescription className="space-y-1 text-sm leading-relaxed">
                      {instructions(
                        status.wizard_step,
                        status.calibration_clicks,
                        status.backend_flags,
                      ).map((line, i) => (
                        <span key={i} className="block">
                          {line}
                        </span>
                      ))}
                    </CardDescription>
                  </motion.div>
                </AnimatePresence>
                <Separator />
                <Button
                  variant="destructive"
                  size="sm"
                  className="w-full"
                  disabled={busy}
                  onClick={hardReset}
                >
                  Reset wizard
                </Button>
                <p className="text-xs text-muted-foreground">
                  Clears calibration, tool 0, and all offsets. Clears any
                  leftover gcode offset transform.
                </p>
              </>
            )}
          </CardContent>
          <CardFooter className="flex flex-row items-center justify-between">
            <Help />
          </CardFooter>
        </Card>

        <Card className="h-fit">
          <CardContent className="space-y-3 h-full">
            {status && (
              <CameraPanel
                ref={cameraRef}
                snapshotUrl={status.snapshot_url}
                ghostSrc={tool0GhostSrc}
                markers={status.markers}
                tool0RefPx={status.tool0_ref_px}
                disabled={busy}
                canUndo={status.can_undo}
                onClick={(px, py) => void cameraClick(px, py)}
                onUndo={handleUndo}
              />
            )}
          </CardContent>
          {cameraFooter && (
            <CardFooter className="flex flex-row items-center justify-between">
              <p className="text-muted-foreground">{cameraFooter.primary}</p>
              {cameraFooter.secondary && (
                <p className="text-xs text-muted-foreground">
                  {cameraFooter.secondary}
                </p>
              )}
            </CardFooter>
          )}
        </Card>

        <Card className="h-full">
          <CardHeader className="space-x-2 flex flex-row items-center justify-between">
            <CardTitle className="text-base">Offsets (mm)</CardTitle>
            {status && <BackendSelect />}
          </CardHeader>
          <Separator />
          <CardContent className="space-y-6">
            {status && (
              <>
                <OffsetsPanel />
                {status.backend_flags.requires_apply_macro && (
                  <p className="text-xs text-muted-foreground">
                    Call APPLY_TOOL_OFFSET TOOL=n from your tool-load macro
                    after Save.
                  </p>
                )}
                <Separator />
                <ActionBar />
              </>
            )}
          </CardContent>
        </Card>
      </main>

      {status && (
        <section className="grid gap-4 p-4 pt-0 lg:grid-cols-2">
          <MotionSettings />
          <MacrosPanel />
        </section>
      )}
    </div>
  );
}
