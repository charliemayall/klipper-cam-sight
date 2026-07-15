"""Wizard session state for klipper-cam-sight."""

from __future__ import annotations

import enum
from dataclasses import dataclass, field

from .geometry import (
    AxisMap,
    PixelPoint,
    calibrate_axis_map,
    tool_offset_from_click,
)


class WizardStep(enum.Enum):
    CALIBRATE = "calibrate"
    TOOL0_REF = "tool0_ref"
    TOOL_OFFSET = "tool_offset"


@dataclass
class Tool0Reference:
    center_px: PixelPoint
    machine_x: float
    machine_y: float

    def to_dict(self) -> dict:
        return {
            "center_px": [self.center_px.x, self.center_px.y],
            "machine_xy": [self.machine_x, self.machine_y],
        }

    @classmethod
    def from_dict(cls, data: dict) -> Tool0Reference:
        cx, cy = data["center_px"]
        mx, my = data["machine_xy"]
        return cls(
            center_px=PixelPoint(float(cx), float(cy)),
            machine_x=float(mx),
            machine_y=float(my),
        )


@dataclass
class CalibrationClicks:
    origin: PixelPoint | None = None
    after_x: PixelPoint | None = None
    after_y: PixelPoint | None = None
    origin_machine_xy: tuple[float, float] | None = None

    @property
    def click_count(self) -> int:
        return sum(
            1 for p in (self.origin, self.after_x, self.after_y) if p is not None
        )

    def reset(self) -> None:
        self.origin = None
        self.after_x = None
        self.after_y = None
        self.origin_machine_xy = None

    def to_dict(self) -> dict:
        out: dict = {}
        if self.origin is not None:
            out["origin"] = [self.origin.x, self.origin.y]
        if self.after_x is not None:
            out["after_x"] = [self.after_x.x, self.after_x.y]
        if self.after_y is not None:
            out["after_y"] = [self.after_y.x, self.after_y.y]
        if self.origin_machine_xy is not None:
            out["origin_machine_xy"] = list(self.origin_machine_xy)
        return out

    @classmethod
    def from_dict(cls, data: dict) -> CalibrationClicks:
        cal = cls()
        if "origin" in data:
            cal.origin = PixelPoint(float(data["origin"][0]), float(data["origin"][1]))
        if "after_x" in data:
            cal.after_x = PixelPoint(
                float(data["after_x"][0]), float(data["after_x"][1])
            )
        if "after_y" in data:
            cal.after_y = PixelPoint(
                float(data["after_y"][0]), float(data["after_y"][1])
            )
        if "origin_machine_xy" in data:
            mx, my = data["origin_machine_xy"]
            cal.origin_machine_xy = (float(mx), float(my))
        return cal


@dataclass
class SessionState:
    wizard_step: WizardStep = WizardStep.CALIBRATE
    axis_map: AxisMap | None = None
    calibration: CalibrationClicks = field(default_factory=CalibrationClicks)
    tool0_ref: Tool0Reference | None = None
    offsets: dict[int, tuple[float, float]] = field(default_factory=dict)
    offset_history: dict[int, list[tuple[float, float]]] = field(default_factory=dict)
    selected_tool: int = 0

    def set_calibration_origin(
        self, px: float, py: float, machine_x: float, machine_y: float
    ) -> None:
        self.calibration.origin = PixelPoint(px, py)
        self.calibration.origin_machine_xy = (machine_x, machine_y)

    def set_calibration_after_x(self, px: float, py: float) -> None:
        self.calibration.after_x = PixelPoint(px, py)

    def set_calibration_after_y(self, px: float, py: float) -> None:
        self.calibration.after_y = PixelPoint(px, py)

    def finish_calibration(self, known_jog_mm: float) -> AxisMap:
        cal = self.calibration
        if cal.origin is None or cal.after_x is None or cal.after_y is None:
            raise RuntimeError("All three calibration picks are required")
        self.axis_map = calibrate_axis_map(
            cal.origin,
            cal.after_x,
            cal.after_y,
            known_jog_mm,
        )
        self.calibration.reset()
        return self.axis_map

    def record_tool0(
        self, px: float, py: float, machine_x: float, machine_y: float
    ) -> None:
        self.tool0_ref = Tool0Reference(PixelPoint(px, py), machine_x, machine_y)
        self.offsets[0] = (0.0, 0.0)

    def clear_tool_offset(self, tool_index: int) -> None:
        if tool_index == 0:
            raise ValueError("Cannot clear tool 0 offset")
        self.offsets.pop(tool_index, None)
        self.offset_history.pop(tool_index, None)

    def reset_tool_offsets(self) -> None:
        for k in [k for k in self.offsets if k != 0]:
            del self.offsets[k]
        for k in [k for k in self.offset_history if k != 0]:
            del self.offset_history[k]
        if self.tool0_ref is not None:
            self.offsets[0] = (0.0, 0.0)

    def apply_tool_click(
        self, tool_index: int, px: float, py: float
    ) -> tuple[tuple[float, float], tuple[float, float]]:
        """Circle center = nozzle here vs T0 pixel. Adds residual to stored offset."""
        if self.tool0_ref is None:
            raise RuntimeError("Tool 0 reference not set")
        if self.axis_map is None:
            raise RuntimeError("Axis map not calibrated")
        residual = tool_offset_from_click(
            self.tool0_ref.center_px,
            PixelPoint(px, py),
            self.axis_map,
        )
        old = self.offsets.get(tool_index, (0.0, 0.0))
        total = (old[0] + residual[0], old[1] + residual[1])
        self.offsets[tool_index] = total
        self.offset_history.setdefault(tool_index, []).append(residual)
        return total, residual

    def undo_tool_offset(self, tool_index: int) -> tuple[float, float] | None:
        """Pop last residual and subtract from total. Returns residual, or None."""
        hist = self.offset_history.get(tool_index)
        if not hist:
            return None
        residual = hist.pop()
        old = self.offsets.get(tool_index, (0.0, 0.0))
        total = (old[0] - residual[0], old[1] - residual[1])
        if hist:
            self.offsets[tool_index] = total
        else:
            self.offsets.pop(tool_index, None)
            self.offset_history.pop(tool_index, None)
        return residual

    def saveable_offsets(self) -> dict[int, tuple[float, float]]:
        """Offsets written by Save - T0 as 0,0 when set; omit uncalibrated tools."""
        out: dict[int, tuple[float, float]] = {}
        if self.tool0_ref is not None:
            out[0] = (0.0, 0.0)
        for k, v in self.offsets.items():
            if k != 0:
                out[k] = v
        return out

    def can_undo(self) -> bool:
        step = self.wizard_step
        if step == WizardStep.CALIBRATE:
            return self.calibration.click_count > 0
        if step == WizardStep.TOOL0_REF:
            return self.tool0_ref is not None
        if step == WizardStep.TOOL_OFFSET:
            tool = self.selected_tool
            if tool == 0:
                return False
            return bool(self.offset_history.get(tool))
        return False

    def undo_last(self) -> tuple[str, tuple[float, float] | None] | None:
        """Pop the last pick. Returns (kind, origin_xy) for calibration moves."""
        step = self.wizard_step
        if step == WizardStep.CALIBRATE:
            cal = self.calibration
            origin_xy = cal.origin_machine_xy
            if cal.after_y is not None:
                cal.after_y = None
                return ("after_y", origin_xy)
            if cal.after_x is not None:
                cal.after_x = None
                return ("after_x", origin_xy)
            if cal.origin is not None:
                xy = cal.origin_machine_xy
                cal.origin = None
                cal.origin_machine_xy = None
                return ("origin", xy)
            return None
        if step == WizardStep.TOOL0_REF:
            if self.tool0_ref is not None:
                self.tool0_ref = None
                self.offsets.pop(0, None)
                return ("tool0", None)
            return None
        if step == WizardStep.TOOL_OFFSET:
            tool = self.selected_tool
            if tool == 0:
                return None
            if self.undo_tool_offset(tool) is not None:
                return (f"tool_{tool}", None)
            return None
        return None

    def to_dict(self) -> dict:
        return {
            "wizard_step": self.wizard_step.value,
            "axis_map": self.axis_map.to_dict() if self.axis_map else None,
            "calibration": self.calibration.to_dict(),
            "tool0_ref": self.tool0_ref.to_dict() if self.tool0_ref else None,
            "offsets": {str(k): [v[0], v[1]] for k, v in self.offsets.items()},
            "offset_history": {
                str(k): [[r[0], r[1]] for r in hist]
                for k, hist in self.offset_history.items()
            },
            "selected_tool": self.selected_tool,
        }

    @classmethod
    def from_dict(cls, data: dict) -> SessionState:
        axis_map = AxisMap.from_dict(data["axis_map"]) if data.get("axis_map") else None
        tool0_ref = (
            Tool0Reference.from_dict(data["tool0_ref"])
            if data.get("tool0_ref")
            else None
        )
        offsets = {
            int(k): (float(v[0]), float(v[1]))
            for k, v in (data.get("offsets") or {}).items()
        }
        offset_history: dict[int, list[tuple[float, float]]] = {}
        for k, rows in (data.get("offset_history") or {}).items():
            offset_history[int(k)] = [(float(r[0]), float(r[1])) for r in rows]
        return cls(
            wizard_step=WizardStep(data.get("wizard_step", WizardStep.CALIBRATE.value)),
            axis_map=axis_map,
            calibration=CalibrationClicks.from_dict(data.get("calibration") or {}),
            tool0_ref=tool0_ref,
            offsets=offsets,
            offset_history=offset_history,
            selected_tool=int(data.get("selected_tool", 0)),
        )

    @classmethod
    def fresh(cls, default_mm_per_pixel: float = 0.0) -> SessionState:
        axis_map = (
            AxisMap.from_mm_per_pixel(default_mm_per_pixel)
            if default_mm_per_pixel > 0
            else None
        )
        step = WizardStep.CALIBRATE
        if axis_map is not None:
            step = WizardStep.TOOL0_REF
        return cls(wizard_step=step, axis_map=axis_map)


def _self_check() -> None:
    from .geometry import calibrate_axis_map

    s = SessionState.fresh()
    s.tool0_ref = Tool0Reference(PixelPoint(100, 100), 150.0, 150.0)
    s.axis_map = calibrate_axis_map(
        PixelPoint(100, 100), PixelPoint(120, 100), PixelPoint(100, 120), 1.0
    )
    s.offsets[0] = (0.0, 0.0)
    s.wizard_step = WizardStep.TOOL_OFFSET
    s.selected_tool = 1

    _, r1 = s.apply_tool_click(1, 96, 93)
    total, r2 = s.apply_tool_click(1, 96, 93)
    assert r1 == r2
    assert total[0] > r1[0] and total[1] > r1[1]
    assert s.can_undo()

    popped = s.undo_tool_offset(1)
    assert popped == r2
    assert s.offsets[1] == r1

    kind, _ = (
        s.undo_last()  # ty:ignore[not-iterable]  # pyright: ignore[reportGeneralTypeIssues]
    )
    assert kind == "tool_1"
    assert 1 not in s.offsets
    assert not s.can_undo()

    s.apply_tool_click(1, 96, 93)
    s.apply_tool_click(1, 96, 93)
    s.undo_tool_offset(1)
    assert 1 in s.offsets
    s.undo_tool_offset(1)
    assert 1 not in s.offsets


_self_check()
