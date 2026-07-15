import { motion, useReducedMotion } from "motion/react";

import { WizardStep, type BackendFlags } from "@/api";
import { cn } from "@/lib/utils";
import { canGoToStep, useSessionStore } from "@/stores/session";

const STEPS: { id: WizardStep; number: number; label: string }[] = [
  { id: WizardStep.CALIBRATE, number: 1, label: "Calibrate" },
  { id: WizardStep.TOOL0_REF, number: 2, label: "Tool 0" },
  { id: WizardStep.TOOL_OFFSET, number: 3, label: "Offset" },
];

const SPRING = { type: "spring" as const, stiffness: 500, damping: 40 };

export interface WizardCompletion {
  calibrate: boolean;
  tool0_ref: boolean;
}

function stepComplete(id: WizardStep, completed: WizardCompletion): boolean {
  if (id === WizardStep.CALIBRATE) return completed.calibrate;
  if (id === WizardStep.TOOL0_REF) return completed.tool0_ref;
  return false;
}

export function WizardNav() {
  const status = useSessionStore((s) => s.status);
  const gotoStep = useSessionStore((s) => s.gotoStep);
  const reduceMotion = useReducedMotion();

  if (!status) return null;

  const current = status.wizard_step;
  const completed: WizardCompletion = {
    calibrate: status.axis_map !== null,
    tool0_ref: status.tool0_machine_xy !== null,
  };
  const transition = reduceMotion ? { duration: 0 } : SPRING;
  const pop = reduceMotion
    ? { duration: 0 }
    : { type: "spring" as const, stiffness: 600, damping: 30 };

  return (
    <nav className="flex w-full items-start" aria-label="Wizard steps">
      {STEPS.map((step, i) => {
        const enabled = canGoToStep(status, step.id);
        const active = current === step.id;
        const complete = stepComplete(step.id, completed);
        const prevComplete = i > 0 && stepComplete(STEPS[i - 1].id, completed);

        return (
          <div key={step.id} className="contents">
            {i > 0 && (
              <div
                className={cn(
                  "mt-4 h-0.5 min-w-2 flex-1 self-start transition-colors duration-300",
                  prevComplete ? "bg-primary" : "bg-border",
                )}
                aria-hidden
              />
            )}
            <button
              type="button"
              disabled={!enabled}
              onClick={() => void gotoStep(step.id)}
              aria-current={active ? "step" : undefined}
              className={cn(
                "flex shrink-0 flex-col items-center gap-1.5 px-0.5",
                enabled ? "cursor-pointer" : "cursor-not-allowed opacity-50",
              )}
            >
              <span className="relative flex size-8 items-center justify-center">
                {active && (
                  <motion.div
                    layoutId="wizard-active-ring"
                    className="absolute inset-0 rounded-full bg-primary"
                    transition={transition}
                  />
                )}
                <motion.span
                  className={cn(
                    "relative z-10 flex size-8 items-center justify-center rounded-full border-2 text-sm font-semibold transition-colors duration-200",
                    active && "border-primary text-primary-foreground",
                    !active &&
                      complete &&
                      "border-primary bg-primary/10 text-primary",
                    !active &&
                      !complete &&
                      "border-muted-foreground/30 text-muted-foreground",
                  )}
                  initial={false}
                  animate={{ scale: 1 }}
                  transition={pop}
                >
                  {step.number}
                </motion.span>
              </span>
              <span
                className={cn(
                  "max-w-18 text-center text-xs leading-tight transition-colors duration-200",
                  active
                    ? "font-medium text-foreground"
                    : "text-muted-foreground",
                )}
              >
                {step.label}
              </span>
            </button>
          </div>
        );
      })}
    </nav>
  );
}

export function instructions(
  step: WizardStep,
  calibrationClicks: number,
  flags?: Pick<BackendFlags, "auto_toolchange">,
): string[] {
  const pick = "Click three points on the nozzle edge to define a circle.";
  switch (step) {
    case WizardStep.CALIBRATE:
      if (calibrationClicks === 0) {
        return [`At the start position, ${pick}`, "Machine jogs +X next."];
      }
      if (calibrationClicks === 1) {
        return [`After the +X jog, ${pick}`, "Returns to start, then jogs +Y."];
      }
      if (calibrationClicks === 2) {
        return [`After the +Y jog, ${pick}`, "Returns to start when done."];
      }
      return [pick];
    case WizardStep.TOOL0_REF:
      return flags?.auto_toolchange
        ? ["Select T0 (auto toolchange), move over the camera.", pick]
        : ["Load tool 0, move over the camera.", pick];
    case WizardStep.TOOL_OFFSET:
      return [
        flags?.auto_toolchange
          ? "Select a tool row - the toolchanger swaps automatically."
          : "Load the selected tool (click a row).",
        "Draw a 3 point circle, with the center being the center of the nozzle.",
        "The machine jogs to the corrected pose.",
        "Circle again if you need to refine.",
        "Save when done.",
        pick,
      ];
  }
}
