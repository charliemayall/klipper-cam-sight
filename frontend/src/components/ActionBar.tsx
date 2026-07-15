import { AnimatePresence, LayoutGroup, motion, useReducedMotion, type MotionProps } from "motion/react";

import { Button } from "@/components/ui/button";
import { selectBusy, useSessionStore } from "@/stores/session";
import { Card, CardContent } from "./ui/card";
import { Separator } from "./ui/separator";
import { WizardStep } from "@/api";

export function ActionBar() {
  const status = useSessionStore((s) => s.status);
  const busy = useSessionStore(selectBusy);
  const moveToCamera = useSessionStore((s) => s.moveToCamera);
  const moveToTool0 = useSessionStore((s) => s.moveToTool0);
  const jogZ = useSessionStore((s) => s.jogZ);
  const reduceMotion = useReducedMotion();

  const showMoveTool0 = status?.wizard_step === WizardStep.TOOL_OFFSET;
  const transition: MotionProps["transition"] = reduceMotion
    ? { type: "spring" as const, duration: 0 }
    : { type: "spring" as const, duration: 0.2 } as const;

  return (
    <Card> 
      <CardContent className="space-y-2 text-xs">
        <p className="text-muted-foreground">Jog:</p>
        <div className="flex gap-2 flex-row items-center text-center">
          <Button
            variant="secondary"
            className="flex-1"
            size="xs"
            disabled={busy}
            onClick={() => void jogZ(-0.1)}
          >
            - 0.1
          </Button>
          <p className="text-sm mx-4">Z</p>
          <Button
            variant="secondary"
            size="xs"
            className="flex-1"
            disabled={busy}
            onClick={() => void jogZ(0.1)}
          >
            + 0.1
          </Button>
        </div>
        
        <Separator />
        <p className="text-muted-foreground">Move to:</p>
        <LayoutGroup id="move-to-buttons">
          <div className="relative flex flex-row gap-2 overflow-hidden">
            <AnimatePresence mode="popLayout" initial={false}>
              <motion.div
                key="camera"
                layout={!reduceMotion ? "position" : false}
                transition={transition}
                className="flex min-w-0 flex-1"
              >
                <Button
                  className="w-full text-xs"
                  variant="secondary"
                  disabled={busy}
                  onClick={() => void moveToCamera()}
                >
                  Camera
                </Button>
              </motion.div>
              {showMoveTool0 && (
                <motion.div
                  key="move-tool0"
                  initial={{ opacity: 0, x: "100%" }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: "100%" }}
                  transition={transition}
                  className="flex min-w-0 flex-1"
                >
                  <Button
                    variant="secondary"
                    className="w-full text-xs"
                    disabled={busy}
                    onClick={() => void moveToTool0()}
                  >
                    Reference XY
                  </Button>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </LayoutGroup>
        </CardContent>
    </Card>
  );
}
