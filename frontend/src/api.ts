export const WizardStep = {
  CALIBRATE: "calibrate",
  TOOL0_REF: "tool0_ref",
  TOOL_OFFSET: "tool_offset",
} as const;
export type WizardStep = (typeof WizardStep)[keyof typeof WizardStep];

export interface AxisMap {
  mm_per_pixel: number;
  x_angle_deg: number;
  y_angle_deg: number;
  known_jog_mm?: number;
  vx?: [number, number];
  vy?: [number, number];
}

export interface OffsetEntry {
  x: number;
  y: number;
}

export interface BackendFlags {
  auto_toolchange: boolean;
  requires_apply_macro: boolean;
  syncs_tool_count: boolean;
}
export const BackendType = {
  BASE: "base",
  INDX: "indx",
} as const;
export type BackendType = (typeof BackendType)[keyof typeof BackendType];
export interface CamSightStatus {
  wizard_step: WizardStep;
  snapshot_url: string;
  webcam_name: string;
  webcams: string[];
  camera_x: number;
  camera_y: number;
  z_approach: number;
  z_measure: number;
  travel_speed: number;
  known_jog_mm: number;
  macros: string[];
  available_macros: string[];
  busy: boolean;
  axis_map: AxisMap | null;
  calibration_clicks: number;
  can_undo: boolean;
  markers: [number, number][];
  offsets: Record<string, OffsetEntry>;
  selected_tool: number;
  tools: number[];
  tool0_machine_xy: [number, number] | null;
  tool0_ref_px: [number, number] | null;
  offsets_dirty: boolean;
  backend: BackendType;
  backend_flags: BackendFlags;
  detected_backend: BackendType;
  backend_override: BackendType | null;
}

interface MoonrakerResponse<T> {
  result?: T;
  error?: { message?: string };
}

async function request<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const res = await fetch(path, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });
  const body = (await res.json()) as MoonrakerResponse<T> | T;
  if (!res.ok) {
    const wrapped = body as MoonrakerResponse<T>;
    const message =
      wrapped.error?.message ??
      (typeof body === "object" && body !== null && "message" in body
        ? String((body as { message: unknown }).message)
        : res.statusText);
    throw new Error(message);
  }
  if (typeof body === "object" && body !== null && "result" in body) {
    return (body as MoonrakerResponse<T>).result as T;
  }
  return body as T;
}

export const API = {
  status: () => request<CamSightStatus>("/machine/cam_sight/status"),

  calibrateClick: (px: number, py: number) =>
    request<CamSightStatus>("/machine/cam_sight/calibrate/click", {
      method: "POST",
      body: JSON.stringify({ px, py }),
    }),

  undo: () =>
    request<CamSightStatus>("/machine/cam_sight/undo", { method: "POST" }),

  tool0Click: (px: number, py: number) =>
    request<CamSightStatus>("/machine/cam_sight/tool0/click", {
      method: "POST",
      body: JSON.stringify({ px, py }),
    }),

  toolClick: (px: number, py: number, tool_index: number) =>
    request<CamSightStatus>("/machine/cam_sight/tool/click", {
      method: "POST",
      body: JSON.stringify({ px, py, tool_index }),
    }),

  moveToCamera: () =>
    request<CamSightStatus>("/machine/cam_sight/move_to_camera", { method: "POST" }),

  moveToTool0: () =>
    request<CamSightStatus>("/machine/cam_sight/move_to_tool0", { method: "POST" }),

  jogZ: (delta_mm: number) =>
    request<CamSightStatus>("/machine/cam_sight/jog_z", {
      method: "POST",
      body: JSON.stringify({ delta_mm }),
    }),

  saveOffsets: () =>
    request<CamSightStatus>("/machine/cam_sight/save_offsets", { method: "POST" }),

  clearOffset: (tool_index: number) =>
    request<CamSightStatus>("/machine/cam_sight/clear_offset", {
      method: "POST",
      body: JSON.stringify({ tool_index }),
    }),

  reset: () =>
    request<CamSightStatus>("/machine/cam_sight/reset", { method: "POST" }),

  resetAll: () =>
    request<CamSightStatus>("/machine/cam_sight/reset_all", { method: "POST" }),

  emergencyStop: () =>
    request<{ ok: boolean }>("/machine/cam_sight/emergency_stop", {
      method: "POST",
    }),

  selectTool: (tool_index: number) =>
    request<CamSightStatus>("/machine/cam_sight/select_tool", {
      method: "POST",
      body: JSON.stringify({ tool_index }),
    }),

  gotoStep: (step: WizardStep) =>
    request<CamSightStatus>("/machine/cam_sight/goto_step", {
      method: "POST",
      body: JSON.stringify({ step }),
    }),

  selectWebcam: (webcam_name: string) =>
    request<CamSightStatus>("/machine/cam_sight/select_webcam", {
      method: "POST",
      body: JSON.stringify({ webcam_name }),
    }),

  updatePrefs: (prefs: {
    camera_x?: number;
    camera_y?: number;
    z_approach?: number;
    z_measure?: number;
    travel_speed?: number;
    known_jog_mm?: number;
  }) =>
    request<CamSightStatus>("/machine/cam_sight/update_prefs", {
      method: "POST",
      body: JSON.stringify(prefs),
    }),

  setToolCount: (count: number) =>
    request<CamSightStatus>("/machine/cam_sight/set_tool_count", {
      method: "POST",
      body: JSON.stringify({ count }),
    }),

  setMacros: (macros: string[]) =>
    request<CamSightStatus>("/machine/cam_sight/set_macros", {
      method: "POST",
      body: JSON.stringify({ macros }),
    }),

  setBackend: (backend: BackendType) =>
    request<CamSightStatus>("/machine/cam_sight/set_backend", {
      method: "POST",
      body: JSON.stringify({ backend }),
    }),

  runMacro: (name: string) =>
    request<CamSightStatus>("/machine/cam_sight/run_macro", {
      method: "POST",
      body: JSON.stringify({ name }),
    }),
};

export function snapshotSrc(url: string, cacheBust = true): string {
  if (!url) return "";
  let path = url;
  // dev-only - Moonraker returns absolute snapshot URLs; strip origin so Vite /webcam proxy handles them
  if (import.meta.env.DEV && url.startsWith("http")) {
    try {
      const u = new URL(url);
      path = u.pathname + u.search;
    } catch {
      path = url;
    }
  }
  const sep = path.includes("?") ? "&" : "?";
  return cacheBust ? `${path}${sep}_=${Date.now()}` : path;
}

/** Fetch current snapshot frame; caller must revoke the returned object URL. */
export async function captureSnapshotFrame(url: string): Promise<string> {
  const res = await fetch(snapshotSrc(url));
  if (!res.ok) throw new Error("Snapshot capture failed");
  const blob = await res.blob();
  return URL.createObjectURL(blob);
}
