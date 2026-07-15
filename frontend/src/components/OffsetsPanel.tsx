import { useCallback, useLayoutEffect, useRef, useState } from "react";
import { AnimatePresence, motion, useReducedMotion } from "motion/react";

import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { cn } from "@/lib/utils";
import { selectBusy, useSessionStore } from "@/stores/session";
import { X, Minus, Plus } from "lucide-react";

const SPRING = { type: "spring" as const, stiffness: 500, damping: 40 };

export function OffsetsPanel() {
  const status = useSessionStore((s) => s.status);
  const busy = useSessionStore(selectBusy);
  const selectTool = useSessionStore((s) => s.selectTool);
  const clearOffset = useSessionStore((s) => s.clearOffset);
  const saveOffsets = useSessionStore((s) => s.saveOffsets);
  const setToolCount = useSessionStore((s) => s.setToolCount);
  const reduceMotion = useReducedMotion();

  const containerRef = useRef<HTMLDivElement>(null);
  const rowRefs = useRef(new Map<number, HTMLTableRowElement>());
  const [bar, setBar] = useState<{ top: number; height: number } | null>(null);

  const selectedTool = status?.selected_tool;
  const tools = status?.tools;

  const measureBar = useCallback(() => {
    if (selectedTool === undefined) return;
    const row = rowRefs.current.get(selectedTool);
    const container = containerRef.current;
    if (!row || !container) return;
    const c = container.getBoundingClientRect();
    const r = row.getBoundingClientRect();
    setBar({ top: r.top - c.top, height: r.height });
  }, [selectedTool, tools]);

  useLayoutEffect(() => {
    measureBar();
    const container = containerRef.current;
    if (!container) return;
    const ro = new ResizeObserver(measureBar);
    ro.observe(container);
    for (const row of Array.from(rowRefs.current.values())) ro.observe(row);
    window.addEventListener("resize", measureBar);
    return () => {
      ro.disconnect();
      window.removeEventListener("resize", measureBar);
    };
  }, [measureBar]);

  if (!status) return null;

  const tool0Ready = status.tool0_machine_xy !== null;
  const transition = reduceMotion ? { duration: 0 } : SPRING;
  const fade = reduceMotion ? { duration: 0 } : { duration: 0.15 };

  const toolCount = status.tools.length;
  const maxTools = 16;

  return (
    <div className="space-y-4">
      <div ref={containerRef} className="relative">
        {bar && (
          <motion.div
            aria-hidden
            className="pointer-events-none absolute left-0 z-10 w-1 rounded-r bg-primary"
            animate={{ top: bar.top, height: bar.height }}
            initial={false}
            transition={transition}
          />
        )}
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Tool</TableHead>
              <TableHead className="text-right">X</TableHead>
              <TableHead className="text-right">Y</TableHead>
              <TableHead className="w-10" />
            </TableRow>
          </TableHeader>
          <TableBody>
            {status.tools.map((toolNum) => {
              const off = status.offsets[String(toolNum)];
              const calibrated = off !== undefined;
              const selected = toolNum === status.selected_tool;
              const selectable = toolNum === 0 || tool0Ready;
              return (
                <TableRow
                  key={toolNum}
                  ref={(el) => {
                    if (el) rowRefs.current.set(toolNum, el);
                    else rowRefs.current.delete(toolNum);
                  }}
                  aria-selected={selected}
                  aria-disabled={!selectable || undefined}
                  data-state={selected ? "selected" : undefined}
                  title={
                    !selectable
                      ? "Set tool 0 reference before selecting other tools"
                      : undefined
                  }
                  className={cn(
                    "transition-colors duration-200 text-muted-foreground",
                    selectable
                      ? "cursor-pointer hover:bg-muted/40"
                      : "cursor-not-allowed opacity-50",
                    selected &&
                      selectable &&
                      "bg-primary/15 hover:bg-primary/20 data-[state=selected]:bg-primary/15",
                  )}
                  onClick={() =>
                    selectable && !busy && void selectTool(toolNum)
                  }
                >
                  <TableCell
                    className={cn(selected && "font-semibold text-foreground")}
                  >
                    T{toolNum}
                  </TableCell>
                  <TableCell className="text-right font-mono text-sm">
                    {calibrated ? (
                      <>
                        {off.x >= 0 ? "+" : ""}
                        {off.x.toFixed(4)}
                      </>
                    ) : (
                      <span className="text-muted-foreground">-</span>
                    )}
                  </TableCell>
                  <TableCell className="text-right font-mono text-sm">
                    {calibrated ? (
                      <>
                        {off.y >= 0 ? "+" : ""}
                        {off.y.toFixed(4)}
                      </>
                    ) : (
                      <span className="text-muted-foreground">-</span>
                    )}
                  </TableCell>
                  <TableCell className="text-right">
                    {toolNum !== 0 && calibrated && (
                      <Button
                        variant="ghost"
                        size="icon"
                        className="size-7 text-destructive hover:text-destructive"
                        aria-label={`Clear T${toolNum} offset`}
                        disabled={busy}
                        onClick={(e) => {
                          e.stopPropagation();
                          void clearOffset(toolNum);
                        }}
                      >
                        <X className="size-4" />
                      </Button>
                    )}
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
        <div className="flex flex-row gap-1 pt-1 w-full justify-end">
          <Button
            variant="secondary"
            size="icon-xs"
            aria-label="Remove tool"
            title="Remove last tool"
            disabled={busy || toolCount <= 1}
            onClick={() => void setToolCount(toolCount - 1)}
          >
            <Minus className="size-3" />
          </Button>
          <Button
            variant="secondary"
            size="icon-xs"
            aria-label="Add tool"
            title="Add new tool"
            disabled={busy || toolCount >= maxTools}
            onClick={() => void setToolCount(toolCount + 1)}
          >
            <Plus className="size-3" />
          </Button>
        </div>
      </div>

      <AnimatePresence>
        {status.offsets_dirty && (
          <motion.div
            key="save-offsets"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 8 }}
            transition={fade}
          >
            <Button
              className="w-full"
              disabled={busy}
              onClick={() => void saveOffsets()}
            >
              Save
            </Button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
