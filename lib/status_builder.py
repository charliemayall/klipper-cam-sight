"""Assemble Cam Sight status payload for the frontend."""

from __future__ import annotations

from typing import Any

from lib.session import SessionState, WizardStep
from lib.tool_backend import ToolBackend


def build_status_dict(
    *,
    session: SessionState,
    snapshot_url: str,
    webcam_name: str,
    webcams: list[str],
    camera_x: float,
    camera_y: float,
    z_approach: float,
    z_measure: float,
    travel_speed: int,
    known_jog_mm: float,
    macros: list[str],
    available_macros: list[str],
    busy: bool,
    tool_count: int,
    offsets_dirty: bool,
    detected_backend_id: str,
    backend_override: str | None,
    backend: ToolBackend,
) -> dict[str, Any]:
    cal = session.calibration
    markers: list[list[float]] = []
    if cal.origin is not None:
        markers.append([cal.origin.x, cal.origin.y])
    if cal.after_x is not None:
        markers.append([cal.after_x.x, cal.after_x.y])
    if cal.after_y is not None:
        markers.append([cal.after_y.x, cal.after_y.y])
    tool0_ref_px: list[float] | None = None
    if session.tool0_ref is not None:
        p = session.tool0_ref.center_px
        markers.append([p.x, p.y])
        tool0_ref_px = [p.x, p.y]

    return {
        "wizard_step": (
            session.wizard_step.value if session.wizard_step else None
        ),
        "snapshot_url": snapshot_url,
        "webcam_name": webcam_name,
        "webcams": webcams,
        "camera_x": camera_x,
        "camera_y": camera_y,
        "z_approach": z_approach,
        "z_measure": z_measure,
        "travel_speed": travel_speed,
        "known_jog_mm": known_jog_mm,
        "macros": list(macros),
        "available_macros": list(available_macros),
        "busy": busy,
        "axis_map": (
            session.axis_map.to_dict() if session.axis_map else None
        ),
        "calibration_clicks": (
            cal.click_count if session.wizard_step == WizardStep.CALIBRATE else 0
        ),
        "can_undo": session.can_undo(),
        "markers": markers,
        "tool0_ref_px": tool0_ref_px,
        "offsets": {
            str(k): {"x": v[0], "y": v[1]}
            for k, v in sorted(session.offsets.items())
        },
        "selected_tool": session.selected_tool,
        "tools": list(range(tool_count)),
        "tool0_machine_xy": (
            [session.tool0_ref.machine_x, session.tool0_ref.machine_y]
            if session.tool0_ref
            else None
        ),
        "offsets_dirty": offsets_dirty,
        "detected_backend": detected_backend_id,
        "backend_override": backend_override,
        **backend.status_dict(),
    }
