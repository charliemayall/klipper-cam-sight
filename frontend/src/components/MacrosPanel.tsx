import { useCallback, useEffect, useLayoutEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { Plus, X } from "lucide-react";
import { toast } from "sonner";

import { EditLockButton } from "@/components/EditLockButton";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import { selectBusy, useSessionStore } from "@/stores/session";
import { Separator } from "./ui/separator";
import { AnimatePresence, LayoutGroup, motion, useReducedMotion } from "motion/react";

const MACRO_NAME_RE = /^[A-Za-z_][A-Za-z0-9_]*$/;

function macroSuggestions(
  query: string,
  available: string[],
  added: string[],
): string[] {
  const q = query.trim().toLowerCase();
  const addedSet = new Set(added);
  return available
    .filter((name) => !addedSet.has(name))
    .filter((name) => !q || name.toLowerCase().includes(q))
    .slice(0, 12);
}

export function MacrosPanel() {
  const status = useSessionStore((s) => s.status);
  const busy = useSessionStore(selectBusy);
  const setMacros = useSessionStore((s) => s.setMacros);
  const runMacro = useSessionStore((s) => s.runMacro);

  const [locked, setLocked] = useState(true);
  const [newMacro, setNewMacro] = useState("");
  const [open, setOpen] = useState(false);
  const [activeIdx, setActiveIdx] = useState(0);
  const [listStyle, setListStyle] = useState<React.CSSProperties | null>(null);
  const inputWrapRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const anchorRef = useRef<HTMLDivElement>(null);
  const listRef = useRef<HTMLUListElement>(null);

  const macros = status?.macros ?? [];
  const available = status?.available_macros ?? [];
  const suggestions = macroSuggestions(newMacro, available, macros);
  const reduceMotion = useReducedMotion();
  const macroTransition = reduceMotion
    ? { duration: 0 }
    : { type: "spring" as const, stiffness: 350, damping: 30 };

  const updateListPosition = useCallback(() => {
    const el = anchorRef.current;
    if (!el) return;
    const r = el.getBoundingClientRect();
    setListStyle({
      position: "fixed",
      left: r.left,
      width: r.width,
      bottom: window.innerHeight - r.top + 4,
      zIndex: 50,
    });
  }, []);

  useLayoutEffect(() => {
    if (!open || suggestions.length === 0) {
      setListStyle(null);
      return;
    }
    updateListPosition();
    window.addEventListener("resize", updateListPosition);
    window.addEventListener("scroll", updateListPosition, true);
    return () => {
      window.removeEventListener("resize", updateListPosition);
      window.removeEventListener("scroll", updateListPosition, true);
    };
  }, [open, suggestions.length, updateListPosition]);

  useEffect(() => {
    if (!open) return;
    const onPointerDown = (e: PointerEvent) => {
      const target = e.target as Node;
      if (
        inputWrapRef.current?.contains(target) ||
        listRef.current?.contains(target)
      ) {
        return;
      }
      setOpen(false);
    };
    document.addEventListener("pointerdown", onPointerDown);
    return () => document.removeEventListener("pointerdown", onPointerDown);
  }, [open]);

  useEffect(() => {
    setActiveIdx(0);
  }, [newMacro, suggestions.length]);

  if (!status) return null;

  const toggleLock = () => {
    setLocked((prev) => {
      if (!prev) {
        setNewMacro("");
        setOpen(false);
      }
      return !prev;
    });
  };

  const addMacro = (nameOverride?: string) => {
    const name = (nameOverride ?? newMacro).trim();
    if (!name) return;
    if (!MACRO_NAME_RE.test(name)) {
      toast.error("Macro name: letters, numbers, underscore; start with letter or _");
      return;
    }
    if (macros.includes(name)) {
      toast.error("Macro already added");
      return;
    }
    setNewMacro("");
    setOpen(false);
    void setMacros([...macros, name]);
  };

  const removeMacro = (name: string) => {
    void setMacros(macros.filter((m) => m !== name));
  };

  return (
    <Card className="relative">
      <EditLockButton locked={locked} label="macros" onToggle={toggleLock} />
      <CardHeader className="flex flex-row mr-12 items-start gap-2 min-h-10">
        <CardTitle className="text-base shrink-0 ">Macros</CardTitle>
        <div
          ref={inputWrapRef}
          className="flex min-w-0 flex-1 items-center justify-end"
        >
          <div ref={anchorRef} className="flex min-w-48 w-full max-w-sm items-center bg-secondary rounded-lg">
            <Input
              ref={inputRef}
              type="text"
              className="h-6 flex-1 rounded-r-none"
              placeholder="e.g. LOAD_TOOL_0"
              disabled={busy}
              value={newMacro}
              role="combobox"
              autoComplete="off"
              aria-expanded={open && suggestions.length > 0}
              aria-autocomplete="list"
              aria-controls="macro-suggestions"
              onChange={(e) => {
                setNewMacro(e.target.value);
                setOpen(true);
              }}
              onFocus={() => setOpen(true)}
              onKeyDown={(e) => {
                if (e.key === "ArrowDown") {
                  if (!open || suggestions.length === 0) return;
                  e.preventDefault();
                  setOpen(true);
                  setActiveIdx((i) => Math.min(i + 1, suggestions.length - 1));
                  return;
                }
                if (e.key === "ArrowUp") {
                  if (!open || suggestions.length === 0) return;
                  e.preventDefault();
                  setActiveIdx((i) => Math.max(i - 1, 0));
                  return;
                }
                if (e.key === "Escape") {
                  setOpen(false);
                  return;
                }
                if (e.key === "Enter") {
                  e.preventDefault();
                  if (open && suggestions[activeIdx]) {
                    addMacro(suggestions[activeIdx]);
                  } else {
                    addMacro();
                  }
                }
              }}
            />
            <Button
              size="sm"
              variant="secondary"
              className="h-6 shrink-0 rounded-l-none"
              disabled={busy}
              onClick={() => addMacro()}
            >
              <Plus className="size-3" />
            </Button>
          </div>
          {open &&
            suggestions.length > 0 &&
            listStyle &&
            createPortal(
              <ul
                ref={listRef}
                id="macro-suggestions"
                role="listbox"
                style={listStyle}
                className="max-h-48 overflow-y-auto rounded-t-lg rounded-b-sm border border-border bg-popover py-1 text-sm shadow-md"
              >
                {suggestions.map((name, idx) => (
                  <>
                  <li
                    key={name}
                    role="option"
                    aria-selected={idx === activeIdx}
                    className={cn(
                      "cursor-pointer px-2.5 py-1.5 font-mono text-xs text-muted-foreground",
                      idx === activeIdx && "bg-accent text-accent-foreground",
                    )}
                    onMouseDown={(e) => e.preventDefault()}
                    onMouseEnter={() => setActiveIdx(idx)}
                    onClick={() => {
                      addMacro(name);
                      inputRef.current?.blur();
                    }}
                  >
                    {name}
                  </li>
                  <Separator key={`separator-${name}`} />
                  </>
                ))}
              </ul>,
              document.body,
            )}
        </div>
      </CardHeader>
      <CardContent className="space-y-1">
        {macros.length > 0 ? (
          <LayoutGroup id="macro-chips">
            <div className="flex flex-wrap gap-1">
              <AnimatePresence mode="popLayout" initial={false}>
                {macros.map((name) => (
                  <motion.div
                    key={name}
                    layout={!reduceMotion ? "position" : false}
                    className="flex items-center justify-center"
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    transition={macroTransition}
                  >
                  <Button
                    size="sm"
                    variant="secondary"
                    disabled={busy}
                    className={locked ? "" : "rounded-r-none"}
                    onClick={() => void runMacro(name)}
                  >
                    {name}
                  </Button>
                  {!locked && (
                    <Button
                      size="icon-sm"
                      variant="destructive"
                      className="size-6 text-muted-foreground rounded-l-none"
                      disabled={busy}
                      aria-label={`Remove ${name}`}
                      onClick={() => removeMacro(name)}
                    >
                      <X className="size-3.5 text-destructive" />
                    </Button>
                  )}
                </motion.div>
                ))}
              </AnimatePresence>
            </div>
          </LayoutGroup>
        ) : (
          <p className="text-xs text-muted-foreground">
            {available.length > 0
              ? "Pick a Klipper macro from the list or type a name."
              : "Add Klipper macro names for one-click shortcuts."}
          </p>
        )}
      </CardContent>
    </Card>
  );
}
