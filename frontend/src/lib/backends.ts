import { BackendType } from "@/api";

export interface BackendInfo {
  label: string;
  title: string;
  summary: string;
  bullets: string[];
}

export const BACKEND_OPTIONS = [BackendType.BASE, BackendType.INDX] as const;

export const BACKEND_INFO: Record<BackendType, BackendInfo> = {
  [BackendType.BASE]: {
    label: "Base",
    title: "Manual toolchange",
    summary:
      "Load each tool yourself. Cam Sight saves offsets to cam_sight_t{n}_* variables.",
    bullets: [
      "Call APPLY_TOOL_OFFSET TwOOL=n from your tool-load macro after Save.",
      "Uses cam_sight_t{n}_x / cam_sight_t{n}_y in save_variables.",
      "Tool count is set with +/- in the offsets panel.",
    ],
  },
  [BackendType.INDX]: {
    label: "INDX",
    title: "INDX toolchanger",
    summary:
      "For printers with an [indx] section. Cam Sight runs CHANGE_TOOL when you pick a tool row and writes t{n}_offset_* variables.",
    bullets: [
      "Auto toolchange when selecting a tool in the wizard.",
      "Syncs tool count from TOOL_POSITIONS when available.",
      "Offsets apply on pickup - no APPLY_TOOL_OFFSET macro needed.",
    ],
  },
};

export function backendLabel(type: BackendType): string {
  return BACKEND_INFO[type].label;
}
