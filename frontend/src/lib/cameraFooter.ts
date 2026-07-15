import { WizardStep, type CamSightStatus } from "@/api";
import { instructions } from "@/components/WizardNav";

export function cameraCardFooter(status: CamSightStatus): {
  primary: string;
  secondary: string | null;
} {
  const primary =
    status.wizard_step === WizardStep.CALIBRATE
      ? `Calibration picks: ${status.calibration_clicks}/3`
      : (instructions(
          status.wizard_step,
          status.calibration_clicks,
          status.backend_flags,
        )[0] ?? "");

  const map = status.axis_map;
  const secondary = map
    ? `${map.mm_per_pixel.toFixed(6)} mm/px · X ${map.x_angle_deg.toFixed(0)}° · Y ${map.y_angle_deg.toFixed(0)}°`
    : null;

  return { primary, secondary };
}
