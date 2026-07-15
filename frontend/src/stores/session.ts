import { toast } from "sonner";
import { create } from "zustand";

import {
  captureSnapshotFrame,
  type BackendType,
  type CamSightStatus,
  type WizardStep,
} from "@/api";
import {
  camSight,
  canGoToStep,
  type MutationResult,
} from "@/lib/camSightClient";

export { canGoToStep };

// module-level ref - blob URLs aren't serializable in store state
let tool0GhostBlobRef: string | null = null;

function revokeGhostBlob() {
  if (tool0GhostBlobRef) {
    URL.revokeObjectURL(tool0GhostBlobRef);
    tool0GhostBlobRef = null;
  }
}

function setGhostSrc(
  set: (partial: Partial<SessionState>) => void,
  src: string | null,
) {
  revokeGhostBlob();
  if (src) tool0GhostBlobRef = src;
  set({ tool0GhostSrc: src });
}

export function selectBusy(s: SessionState): boolean {
  return s.loading || (s.status?.busy ?? false);
}

interface SessionState {
  status: CamSightStatus | null;
  loading: boolean;
  error: string | null;
  tool0GhostSrc: string | null;

  refresh: () => Promise<void>;
  run: (fn: () => Promise<MutationResult>) => Promise<void>;

  gotoStep: (step: WizardStep) => Promise<void>;
  hardReset: () => void;
  moveToCamera: () => Promise<void>;
  moveToTool0: () => Promise<void>;

  cameraClick: (px: number, py: number) => Promise<void>;
  undo: (tryLocalUndo?: () => boolean) => Promise<void>;

  selectTool: (tool: number) => Promise<void>;
  clearOffset: (tool: number) => Promise<void>;
  resetOffsets: () => Promise<void>;
  saveOffsets: () => Promise<void>;
  jogZ: (delta: number) => Promise<void>;

  selectWebcam: (name: string) => Promise<void>;
  updatePrefs: (prefs: {
    camera_x?: number;
    camera_y?: number;
    z_approach?: number;
    z_measure?: number;
    travel_speed?: number;
    known_jog_mm?: number;
  }) => Promise<void>;
  setToolCount: (count: number) => Promise<void>;
  setMacros: (macros: string[]) => Promise<void>;
  runMacro: (name: string) => Promise<void>;

  syncGhostFromStatus: () => void;

  setBackend: (type: BackendType) => Promise<void>;
}

export const useSessionStore = create<SessionState>((set, get) => ({
  status: null,
  loading: false,
  error: null,
  tool0GhostSrc: null,

  refresh: async () => {
    try {
      const s = await camSight.status();
      set({ status: s, error: null });
      get().syncGhostFromStatus();
    } catch (e) {
      set({
        error: e instanceof Error ? e.message : "Failed to load status",
      });
    }
  },

  run: async (fn) => {
    set({ loading: true });
    try {
      const { status, message } = await fn();
      set({ status });
      if (message) toast.success(message);
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Request failed");
    } finally {
      set({ loading: false });
    }
  },

  gotoStep: async (step) => {
    const { status } = get();
    if (!status || status.wizard_step === step) return;
    try {
      const { status: next } = await camSight.gotoStep(step);
      set({ status: next });
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Request failed");
    }
  },

  hardReset: () => {
    if (
      !window.confirm(
        "Reset the entire wizard? Clears mm/px calibration, tool 0 reference, and all tool offsets. This cannot be undone.",
      )
    ) {
      return;
    }
    void (async () => {
      set({ loading: true });
      try {
        const { status, message } = await camSight.resetAll();
        set({ status });
        setGhostSrc(set, null);
        if (message) toast.success(message);
      } catch (e) {
        toast.error(e instanceof Error ? e.message : "Request failed");
      } finally {
        set({ loading: false });
      }
    })();
  },

  moveToCamera: () => get().run(() => camSight.moveToCamera()),

  moveToTool0: () => get().run(() => camSight.moveToTool0()),

  cameraClick: async (px, py) => {
    const { status, loading } = get();
    if (!status || status.busy || loading) return;

    set({ loading: true });
    try {
      const outcome = await camSight.cameraClick(status, px, py);
      if (outcome.kind === "mutation") {
        set({ status: outcome.result.status });
        if (outcome.result.message) toast.success(outcome.result.message);
        return;
      }
      set({ status: outcome.result.status });
      if (outcome.result.message) toast.success(outcome.result.message);
      try {
        setGhostSrc(set, await captureSnapshotFrame(outcome.snapshotUrl));
      } catch {
        // ghost is optional - live feed still works without a frozen frame
      }
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Request failed");
    } finally {
      set({ loading: false });
    }
  },

  undo: async (tryLocalUndo) => {
    if (tryLocalUndo?.()) return;
    const { status, loading, run } = get();
    if (!status || status.busy || loading || !status.can_undo) return;
    await run(() => camSight.undo());
  },

  selectTool: (tool) => {
    const { status } = get();
    if (!status) return Promise.resolve();
    if (tool !== 0 && status.tool0_machine_xy === null) return Promise.resolve();
    return get().run(() => camSight.selectTool(tool));
  },

  clearOffset: (tool) => get().run(() => camSight.clearOffset(tool)),

  resetOffsets: () => get().run(() => camSight.resetOffsets()),

  saveOffsets: () => get().run(() => camSight.saveOffsets()),

  jogZ: (delta) => get().run(() => camSight.jogZ(delta)),

  selectWebcam: (name) => get().run(() => camSight.selectWebcam(name)),

  updatePrefs: (prefs) => get().run(() => camSight.updatePrefs(prefs)),

  setToolCount: (count) => get().run(() => camSight.setToolCount(count)),

  setMacros: async (macros) => {
    const prev = get().status;
    if (!prev) return;
    set({ status: { ...prev, macros } });
    try {
      const { status } = await camSight.setMacros(macros);
      set({ status });
    } catch (e) {
      set({ status: prev });
      toast.error(e instanceof Error ? e.message : "Request failed");
    }
  },

  runMacro: (name) => get().run(() => camSight.runMacro(name)),

  setBackend: (type) => get().run(() => camSight.setBackend(type)),

  syncGhostFromStatus: () => {
    const { status } = get();
    if (status?.tool0_machine_xy === null && tool0GhostBlobRef) {
      setGhostSrc(set, null);
    }
  },
}));

export function disposeSessionGhost() {
  revokeGhostBlob();
}
