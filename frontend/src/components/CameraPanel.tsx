import {
  forwardRef,
  useCallback,
  useEffect,
  useImperativeHandle,
  useRef,
  useState,
} from "react";
import { AnimatePresence, motion, useReducedMotion } from "motion/react";
import { Ghost, Undo2 } from "lucide-react";

import { snapshotSrc } from "@/api";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { cn } from "@/lib/utils";

interface CameraPanelProps {
  snapshotUrl: string;
  ghostSrc?: string | null;
  markers: [number, number][];
  tool0RefPx?: [number, number] | null;
  disabled?: boolean;
  canUndo?: boolean;
  onClick: (px: number, py: number) => void;
  onUndo?: () => void;
}

export interface CameraPanelHandle {
  undoLocalPick: () => boolean;
}

interface PixelPoint {
  x: number;
  y: number;
}

interface Circle {
  center: PixelPoint;
  radius: number;
}

const REFRESH_MS = 250;
const SNAPSHOT_TIMEOUT_MS = 10_000;
const MIN_CIRCLE_AREA = 4;
const TOOL0_CROSSHAIR_ARM = 60;
const POP = { type: "spring" as const, stiffness: 600, damping: 30 };

function circleFrom3Points(
  a: PixelPoint,
  b: PixelPoint,
  c: PixelPoint,
): Circle | null {
  const d = 2 * (a.x * (b.y - c.y) + b.x * (c.y - a.y) + c.x * (a.y - b.y));
  if (Math.abs(d) < MIN_CIRCLE_AREA) return null;

  const a2 = a.x * a.x + a.y * a.y;
  const b2 = b.x * b.x + b.y * b.y;
  const c2 = c.x * c.x + c.y * c.y;

  const cx = (a2 * (b.y - c.y) + b2 * (c.y - a.y) + c2 * (a.y - b.y)) / d;
  const cy = (a2 * (c.x - b.x) + b2 * (a.x - c.x) + c2 * (b.x - a.x)) / d;

  return {
    center: { x: cx, y: cy },
    radius: Math.hypot(cx - a.x, cy - a.y),
  };
}

export const CameraPanel = forwardRef<CameraPanelHandle, CameraPanelProps>(
  function CameraPanel(
    {
      snapshotUrl,
      ghostSrc,
      markers,
      tool0RefPx,
      disabled,
      canUndo = false,
      onClick,
      onUndo,
    },
    ref,
  ) {
    const imgRef = useRef<HTMLImageElement>(null);
    const probeInFlight = useRef(false);
    const [src, setSrc] = useState("");
    const [dims, setDims] = useState({ w: 0, h: 0 });
    const [points, setPoints] = useState<PixelPoint[]>([]);
    const [hover, setHover] = useState<PixelPoint | null>(null);
    const [ghostVisible, setGhostVisible] = useState(false);
    const reduceMotion = useReducedMotion();
    const pop = reduceMotion ? { duration: 0 } : POP;
    const fade = reduceMotion ? { duration: 0 } : { duration: 0.12 };

    const refresh = useCallback(() => {
      if (!snapshotUrl || probeInFlight.current) return;
      probeInFlight.current = true;
      const next = snapshotSrc(snapshotUrl);
      const probe = new Image();
      let settled = false;
      const release = () => {
        if (settled) return;
        settled = true;
        probeInFlight.current = false;
      };
      const timer = window.setTimeout(release, SNAPSHOT_TIMEOUT_MS);
      probe.onload = () => {
        window.clearTimeout(timer);
        setSrc(next);
        release();
      };
      probe.onerror = () => {
        window.clearTimeout(timer);
        release();
      };
      probe.src = next;
    }, [snapshotUrl]);

    // pause live refresh while placing circle points - src swaps steal trackpad taps
    useEffect(() => {
      refresh();
      if (points.length > 0) return;
      const id = setInterval(refresh, REFRESH_MS);
      return () => clearInterval(id);
    }, [refresh, points.length]);

    const resetPick = useCallback(() => {
      setPoints([]);
      setHover(null);
    }, []);

    useEffect(() => {
      if (disabled) resetPick();
    }, [disabled, resetPick]);

    useImperativeHandle(
      ref,
      () => ({
        undoLocalPick: () => {
          if (points.length === 0) return false;
          setPoints((prev) => prev.slice(0, -1));
          setHover(null);
          return true;
        },
      }),
      [points.length],
    );

    const toImagePx = useCallback(
      (clientX: number, clientY: number): PixelPoint | null => {
        const img = imgRef.current;
        if (!img) return null;
        const w = img.naturalWidth || dims.w;
        const h = img.naturalHeight || dims.h;
        if (!w || !h) return null;
        const rect = img.getBoundingClientRect();
        return {
          x: (clientX - rect.left) * (w / rect.width),
          y: (clientY - rect.top) * (h / rect.height),
        };
      },
      [dims.w, dims.h],
    );

    const commitCircle = useCallback(
      (p1: PixelPoint, p2: PixelPoint, p3: PixelPoint) => {
        const circle = circleFrom3Points(p1, p2, p3);
        if (!circle) return false;
        onClick(circle.center.x, circle.center.y);
        resetPick();
        return true;
      },
      [onClick, resetPick],
    );

    const handlePointerDown = (e: React.PointerEvent<HTMLImageElement>) => {
      if (disabled || e.button !== 0) return;
      e.preventDefault();
      const pt = toImagePx(e.clientX, e.clientY);
      if (!pt) return;

      if (points.length < 2) {
        setPoints((prev) => [...prev, pt]);
        return;
      }

      if (points.length === 2) {
        commitCircle(points[0], points[1], pt);
      }
    };

    const handlePointerMove = (e: React.PointerEvent<HTMLImageElement>) => {
      if (disabled || points.length !== 2) return;
      setHover(toImagePx(e.clientX, e.clientY));
    };

    const handlePointerLeave = () => setHover(null);

    const handleLoad = () => {
      const img = imgRef.current;
      if (img) {
        setDims({ w: img.naturalWidth, h: img.naturalHeight });
      }
    };

    const preview =
      points.length === 2 && hover
        ? circleFrom3Points(points[0], points[1], hover)
        : null;

    const markerR = Math.max(6, dims.w * 0.008);
    const localPick = points.length > 0;
    const showUndo = !disabled && (localPick || canUndo);
    const showGhost = ghostVisible && !!ghostSrc;

    const releaseGhost = useCallback(() => setGhostVisible(false), []);

    return (
      <div className="space-y-2">
        <div className="relative overflow-hidden rounded-lg border bg-muted/30">
          {src ? (
            <div className="relative inline-block w-full">
              <AnimatePresence>
                {(showUndo || ghostSrc) && (
                  <motion.div
                    key="camera-toolbar"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={fade}
                    className="absolute top-2 right-2 z-10 flex items-center gap-1 rounded-md bg-secondary/90 p-0.5 shadow-sm"
                  >
                    {ghostSrc && (
                      <Button
                        type="button"
                        variant="ghost"
                        size="icon-sm"
                        className="touch-none select-none"
                        title="Hold for T0 ghost"
                        onPointerDown={(e) => {
                          e.preventDefault();
                          setGhostVisible(true);
                        }}
                        onPointerUp={releaseGhost}
                        onPointerLeave={releaseGhost}
                        onPointerCancel={releaseGhost}
                      >
                        <Ghost />
                      </Button>
                    )}
                    {ghostSrc && showUndo && (
                      <Separator orientation="vertical" className="h-5" />
                    )}
                    {showUndo && (
                      <Button
                        type="button"
                        variant="ghost"
                        size="icon-sm"
                        title="Undo (⌘Z)"
                        onClick={onUndo}
                      >
                        <Undo2 />
                      </Button>
                    )}
                  </motion.div>
                )}
              </AnimatePresence>
              <img
                ref={imgRef}
                src={src}
                alt="Nozzle camera"
                draggable={false}
                onPointerDown={handlePointerDown}
                onPointerMove={handlePointerMove}
                onPointerLeave={handlePointerLeave}
                onLoad={handleLoad}
                className={cn(
                  "block w-full max-h-[70vh] touch-none object-contain select-none",
                  disabled ? "cursor-not-allowed" : "cursor-crosshair",
                )}
              />
              <AnimatePresence>
                {showGhost && (
                  <motion.img
                    key="ghost-overlay"
                    src={ghostSrc!}
                    alt="Tool 0 reference ghost"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 0.4 }}
                    exit={{ opacity: 0 }}
                    transition={fade}
                    className="pointer-events-none absolute inset-0 h-full w-full object-contain"
                  />
                )}
              </AnimatePresence>
              {dims.w > 0 && (
                <svg
                  className="pointer-events-none absolute inset-0 h-full w-full"
                  viewBox={`0 0 ${dims.w} ${dims.h}`}
                  preserveAspectRatio="xMidYMid meet"
                >
                  {markers.map(([x, y], i) => (
                    <motion.circle
                      key={`m-${i}`}
                      cx={x}
                      cy={y}
                      fill="none"
                      stroke="lime"
                      strokeWidth={2}
                      initial={{ r: 0, opacity: 0 }}
                      animate={{ r: markerR, opacity: 1 }}
                      transition={pop}
                    />
                  ))}
                  {tool0RefPx && (
                    <>
                      <line
                        x1={tool0RefPx[0] - TOOL0_CROSSHAIR_ARM}
                        y1={tool0RefPx[1]}
                        x2={tool0RefPx[0] + TOOL0_CROSSHAIR_ARM}
                        y2={tool0RefPx[1]}
                        stroke="lime"
                        strokeWidth={2}
                      />
                      <line
                        x1={tool0RefPx[0]}
                        y1={tool0RefPx[1] - TOOL0_CROSSHAIR_ARM}
                        x2={tool0RefPx[0]}
                        y2={tool0RefPx[1] + TOOL0_CROSSHAIR_ARM}
                        stroke="lime"
                        strokeWidth={2}
                      />
                    </>
                  )}
                  {points.map((p, i) => (
                    <motion.circle
                      key={`p-${i}`}
                      cx={p.x}
                      cy={p.y}
                      fill="lime"
                      initial={{ r: 0, opacity: 0 }}
                      animate={{ r: markerR * 0.6, opacity: 0.8 }}
                      transition={pop}
                    />
                  ))}
                  {preview && (
                    <>
                      <motion.circle
                        cx={preview.center.x}
                        cy={preview.center.y}
                        fill="none"
                        stroke="lime"
                        strokeWidth={2}
                        strokeDasharray="6 4"
                        initial={{ r: 0, opacity: 0.6 }}
                        animate={
                          reduceMotion
                            ? { r: preview.radius, opacity: 0.8 }
                            : {
                                r: preview.radius,
                                opacity: [0.6, 1, 0.6],
                              }
                        }
                        transition={
                          reduceMotion
                            ? pop
                            : {
                                r: pop,
                                opacity: {
                                  duration: 2,
                                  repeat: Infinity,
                                  ease: "easeInOut",
                                },
                              }
                        }
                      />
                      <line
                        x1={preview.center.x - markerR}
                        y1={preview.center.y}
                        x2={preview.center.x + markerR}
                        y2={preview.center.y}
                        stroke="lime"
                        strokeWidth={2}
                      />
                      <line
                        x1={preview.center.x}
                        y1={preview.center.y - markerR}
                        x2={preview.center.x}
                        y2={preview.center.y + markerR}
                        stroke="lime"
                        strokeWidth={2}
                      />
                    </>
                  )}
                </svg>
              )}
            </div>
          ) : (
            <div className="flex h-48 items-center justify-center text-sm text-muted-foreground">
              {snapshotUrl
                ? "Loading camera…"
                : "No snapshot URL - check webcam config"}
            </div>
          )}
        </div>
      </div>
    );
  },
);
