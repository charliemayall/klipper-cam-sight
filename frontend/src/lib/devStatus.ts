import heroSnapshot from "@/assets/hero.png";
import { BackendType, WizardStep, type CamSightStatus } from "@/api";
import { devBackendFlags, getDevBackendType } from "@/lib/devBackend";

const DEV_DETECTED_BACKEND = BackendType.BASE;

/** Fake printer status when `make dev-frontend` cannot reach Moonraker. */
export function devCamSightStatus(): CamSightStatus {
  const backend = getDevBackendType();
  const backend_override =
    backend === DEV_DETECTED_BACKEND ? null : backend;

  return {
    wizard_step: WizardStep.CALIBRATE,
    snapshot_url: heroSnapshot,
    webcam_name: "dev-cam",
    webcams: ["dev-cam", "wide-angle"],
    camera_x: 150,
    camera_y: 200,
    z_approach: 5,
    z_measure: 5,
    travel_speed: 3000,
    known_jog_mm: 20,
    macros: ["PARK", "LOAD_FILAMENT"],
    available_macros: ["PARK", "LOAD_FILAMENT", "M600", "APPLY_TOOL_OFFSET"],
    busy: false,
    axis_map: null,
    calibration_clicks: 0,
    can_undo: false,
    markers: [],
    offsets: {
      "1": { x: 0.12, y: -0.05 },
      "2": { x: 0.31, y: 0.08 },
    },
    selected_tool: 1,
    tools: [0, 1, 2, 3],
    tool0_machine_xy: null,
    tool0_ref_px: null,
    offsets_dirty: false,
    backend,
    backend_flags: devBackendFlags(backend),
    detected_backend: DEV_DETECTED_BACKEND,
    backend_override,
  };
}
