import {
  API,
  type BackendType,
  WizardStep,
  type CamSightStatus,
} from "@/api";
import { setDevBackendType } from "@/lib/devBackend";

export function canGoToStep(status: CamSightStatus, step: WizardStep): boolean {
  if (step === WizardStep.CALIBRATE) return true;
  if (step === WizardStep.TOOL0_REF) return status.axis_map !== null;
  if (step === WizardStep.TOOL_OFFSET) return status.tool0_machine_xy !== null;
  return false;
}

export interface MutationResult {
  status: CamSightStatus;
  message?: string;
}

export type CameraClickResult =
  | { kind: "mutation"; result: MutationResult }
  | { kind: "tool0"; result: MutationResult; snapshotUrl: string };

function calibrationMessage(clickCount: number): string {
  if (clickCount === 0) return "Origin saved - jogging +X";
  if (clickCount === 1) return "+X pick saved - returning, then jogging +Y";
  return "Calibration complete";
}

let devFallbackWarned = false;

/** Domain API layer - wraps raw fetch calls with wizard-specific routing and messages. */
export class CamSightClient {
  private readonly backend: typeof API;

  constructor(backend: typeof API = API) {
    this.backend = backend;
  }

  status(): Promise<CamSightStatus> {
    if (!import.meta.env.DEV) {
      return this.backend.status();
    }
    return this.backend.status().catch(async (err) => {
      if (!devFallbackWarned) {
        console.warn(
          "cam_sight: Moonraker unavailable - using dev fallback status",
          err,
        );
        devFallbackWarned = true;
      }
      const { devCamSightStatus } = await import("@/lib/devStatus");
      return devCamSightStatus();
    });
  }

  setBackend(backend: BackendType): Promise<MutationResult> {
    if (import.meta.env.DEV) {
      return this.backend
        .setBackend(backend)
        .then((status) => ({ status }))
        .catch(async () => {
          setDevBackendType(backend);
          const { devCamSightStatus } = await import("@/lib/devStatus");
          return { status: devCamSightStatus() };
        });
    }
    return this.mutate(() => this.backend.setBackend(backend));
  }

  gotoStep(step: WizardStep): Promise<MutationResult> {
    return this.mutate(() => this.backend.gotoStep(step));
  }

  resetAll(): Promise<MutationResult> {
    return this.mutate(
      () => this.backend.resetAll(),
      "Wizard reset - start from calibration",
    );
  }

  moveToCamera(): Promise<MutationResult> {
    return this.mutate(
      () => this.backend.moveToCamera(),
      "At camera position",
    );
  }

  moveToTool0(): Promise<MutationResult> {
    return this.mutate(() => this.backend.moveToTool0(), "At tool 0 XY");
  }

  undo(): Promise<MutationResult> {
    return this.mutate(() => this.backend.undo(), "Undone");
  }

  selectTool(tool: number): Promise<MutationResult> {
    return this.mutate(() => this.backend.selectTool(tool));
  }

  clearOffset(tool: number): Promise<MutationResult> {
    return this.mutate(
      () => this.backend.clearOffset(tool),
      `T${tool} offset cleared`,
    );
  }

  resetOffsets(): Promise<MutationResult> {
    return this.mutate(
      () => this.backend.reset(),
      "All tool offsets cleared",
    );
  }

  saveOffsets(): Promise<MutationResult> {
    return this.mutate(
      () => this.backend.saveOffsets(),
      "Offsets saved to save_variables",
    );
  }

  jogZ(delta: number): Promise<MutationResult> {
    return this.mutate(() => this.backend.jogZ(delta));
  }

  selectWebcam(name: string): Promise<MutationResult> {
    return this.mutate(
      () => this.backend.selectWebcam(name),
      `Camera: ${name}`,
    );
  }

  updatePrefs(prefs: {
    camera_x?: number;
    camera_y?: number;
    z_approach?: number;
    z_measure?: number;
    travel_speed?: number;
    known_jog_mm?: number;
  }): Promise<MutationResult> {
    return this.mutate(
      () => this.backend.updatePrefs(prefs),
      "Motion settings saved",
    );
  }

  setToolCount(count: number): Promise<MutationResult> {
    return this.mutate(() => this.backend.setToolCount(count));
  }

  setMacros(macros: string[]): Promise<MutationResult> {
    return this.mutate(() => this.backend.setMacros(macros));
  }

  runMacro(name: string): Promise<MutationResult> {
    return this.mutate(() => this.backend.runMacro(name), name);
  }

  emergencyStop(): Promise<{ ok: boolean }> {
    return this.backend.emergencyStop();
  }

  cameraClick(
    status: CamSightStatus,
    px: number,
    py: number,
  ): Promise<CameraClickResult> {
    const step = status.wizard_step;
    if (step === WizardStep.CALIBRATE) {
      return this.mutate(
        () => this.backend.calibrateClick(px, py),
        calibrationMessage(status.calibration_clicks),
      ).then((result) => ({ kind: "mutation", result }));
    }

    if (step === WizardStep.TOOL0_REF) {
      return this.backend.tool0Click(px, py).then((s) => ({
        kind: "tool0",
        result: { status: s, message: "Tool 0 reference saved" },
        snapshotUrl: s.snapshot_url,
      }));
    }

    return this.mutate(
      () => this.backend.toolClick(px, py, status.selected_tool),
      `T${status.selected_tool} offset updated`,
    ).then((result) => ({ kind: "mutation", result }));
  }

  private async mutate(
    fn: () => Promise<CamSightStatus>,
    message?: string,
  ): Promise<MutationResult> {
    return { status: await fn(), message };
  }
}

export const camSight = new CamSightClient();
