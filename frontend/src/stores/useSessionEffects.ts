import { useEffect } from "react";

import { useSessionStore } from "./session";

/** Poll backend status every 2s. Mount once from App. */
export function useSessionPolling() {
  const refresh = useSessionStore((s) => s.refresh);

  useEffect(() => {
    void refresh();
    const id = setInterval(() => void refresh(), 2000);
    return () => clearInterval(id);
  }, [refresh]);
}

/** Warn before closing tab when offsets are unsaved. */
export function useOffsetsDirtyGuard() {
  const dirty = useSessionStore((s) => s.status?.offsets_dirty ?? false);

  useEffect(() => {
    if (!dirty) return;
    const onBeforeUnload = (e: BeforeUnloadEvent) => {
      e.preventDefault();
      e.returnValue = "";
    };
    window.addEventListener("beforeunload", onBeforeUnload);
    return () => window.removeEventListener("beforeunload", onBeforeUnload);
  }, [dirty]);
}
