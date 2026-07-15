"""Pixel ↔ millimetre conversion and axis mapping from calibration clicks."""

from __future__ import annotations

import math
from dataclasses import dataclass

MIN_PIXEL_SHIFT = 2.0
MIN_DET = 1e-6


@dataclass(frozen=True)
class PixelPoint:
    x: float
    y: float


@dataclass(frozen=True)
class AxisMap:
    """Map pixel deltas to machine XY mm using calibrated jog basis vectors."""

    known_jog_mm: float
    vx_x: float  # pixel shift from a +X machine jog
    vx_y: float
    vy_x: float  # pixel shift from a +Y machine jog
    vy_y: float

    @property
    def mm_per_pixel(self) -> float:
        sx = self.known_jog_mm / math.hypot(self.vx_x, self.vx_y)
        sy = self.known_jog_mm / math.hypot(self.vy_x, self.vy_y)
        return (sx + sy) / 2

    @property
    def x_angle_deg(self) -> float:
        return math.degrees(math.atan2(self.vx_y, self.vx_x))

    @property
    def y_angle_deg(self) -> float:
        return math.degrees(math.atan2(self.vy_y, self.vy_x))

    def px_delta_to_mm(self, dx_px: float, dy_px: float) -> tuple[float, float]:
        det = self.vx_x * self.vy_y - self.vx_y * self.vy_x
        if abs(det) < MIN_DET:
            raise ValueError("Calibration X/Y jogs are collinear - recalibrate")
        s = self.known_jog_mm / det
        return (
            s * (self.vy_y * dx_px - self.vy_x * dy_px),
            s * (-self.vx_y * dx_px + self.vx_x * dy_px),
        )

    def to_dict(self) -> dict:
        return {
            "known_jog_mm": self.known_jog_mm,
            "vx": [round(self.vx_x, 4), round(self.vx_y, 4)],
            "vy": [round(self.vy_x, 4), round(self.vy_y, 4)],
            "mm_per_pixel": round(self.mm_per_pixel, 6),
            "x_angle_deg": round(self.x_angle_deg, 1),
            "y_angle_deg": round(self.y_angle_deg, 1),
        }

    @classmethod
    def from_dict(cls, data: dict) -> AxisMap:
        if "vx" in data and "vy" in data:
            vx = data["vx"]
            vy = data["vy"]
            return cls(
                known_jog_mm=float(data.get("known_jog_mm", 1.0)),
                vx_x=float(vx[0]),
                vx_y=float(vx[1]),
                vy_x=float(vy[0]),
                vy_y=float(vy[1]),
            )
        # legacy axis-aligned sessions before full 2D calibration
        mm = float(data["mm_per_pixel"])
        xs = int(data.get("x_sign", 1))
        ys = int(data.get("y_sign", 1))
        jog = float(data.get("known_jog_mm", 1.0))
        return cls(
            known_jog_mm=jog,
            vx_x=xs * jog / mm,
            vx_y=0.0,
            vy_x=0.0,
            vy_y=ys * jog / mm,
        )

    @classmethod
    def from_mm_per_pixel(cls, mm_per_pixel: float) -> AxisMap:
        jog = 1.0
        return cls(
            known_jog_mm=jog,
            vx_x=jog / mm_per_pixel,
            vx_y=0.0,
            vy_x=0.0,
            vy_y=jog / mm_per_pixel,
        )


def calibrate_axis_map(
    origin: PixelPoint,
    after_x: PixelPoint,
    after_y: PixelPoint,
    known_jog_mm: float,
) -> AxisMap:
    """Derive mm/px and machine-axis directions from +X and +Y jog picks."""
    if known_jog_mm <= 0:
        raise ValueError("known_jog_mm must be positive")

    vx_x = after_x.x - origin.x
    vx_y = after_x.y - origin.y
    vy_x = after_y.x - origin.x
    vy_y = after_y.y - origin.y

    if math.hypot(vx_x, vx_y) < MIN_PIXEL_SHIFT:
        raise ValueError(
            f"X calibration: nozzle moved only {math.hypot(vx_x, vx_y):.1f} px "
            f"for a {known_jog_mm} mm jog. Increase known_jog_mm or check the pick."
        )
    if math.hypot(vy_x, vy_y) < MIN_PIXEL_SHIFT:
        raise ValueError(
            f"Y calibration: nozzle moved only {math.hypot(vy_x, vy_y):.1f} px "
            f"for a {known_jog_mm} mm jog. Increase known_jog_mm or check the pick."
        )

    det = vx_x * vy_y - vx_y * vy_x
    if abs(det) < MIN_DET:
        raise ValueError(
            "X and Y calibration jogs are too parallel - pick clearer axis picks"
        )

    return AxisMap(
        known_jog_mm=known_jog_mm,
        vx_x=vx_x,
        vx_y=vx_y,
        vy_x=vy_x,
        vy_y=vy_y,
    )


def tool_offset_from_click(
    tool0_center: PixelPoint,
    click: PixelPoint,
    axis_map: AxisMap,
) -> tuple[float, float]:
    """SET_GCODE_OFFSET XY (mm): tool at -X,-Y relative to T0 → offset +X,+Y."""
    dx_px = tool0_center.x - click.x
    dy_px = tool0_center.y - click.y
    return axis_map.px_delta_to_mm(dx_px, dy_px)


def _self_check() -> None:
    origin = PixelPoint(100, 100)
    m = calibrate_axis_map(origin, PixelPoint(120, 100), PixelPoint(100, 120), 1.0)
    assert math.isclose(m.mm_per_pixel, 0.05)
    assert math.isclose(m.x_angle_deg, 0.0)
    assert math.isclose(m.y_angle_deg, 90.0)
    dx, dy = m.px_delta_to_mm(10, 0)
    assert math.isclose(dx, 0.5) and math.isclose(dy, 0.0)

    m_rev = calibrate_axis_map(origin, PixelPoint(80, 100), PixelPoint(100, 80), 1.0)
    dx, _ = m_rev.px_delta_to_mm(-10, 0)
    assert math.isclose(dx, 0.5)

    m_rot = calibrate_axis_map(origin, PixelPoint(118, 106), PixelPoint(94, 116), 1.0)
    # Round-trip: calibrated jog vectors → 1 mm on each machine axis
    ox, oy = m_rot.px_delta_to_mm(m_rot.vx_x, m_rot.vx_y)
    assert math.isclose(ox, 1.0) and math.isclose(oy, 0.0, abs_tol=1e-6)
    ox, oy = m_rot.px_delta_to_mm(m_rot.vy_x, m_rot.vy_y)
    assert math.isclose(ox, 0.0, abs_tol=1e-6) and math.isclose(oy, 1.0)

    # Tool at machine -X,-Y vs T0 → offset +X,+Y
    off_x, off_y = tool_offset_from_click(PixelPoint(100, 100), PixelPoint(96, 93), m)
    assert off_x > 0 and off_y > 0

    # residual accumulates when refining after jog-to-corrected pose
    prior = (0.2, 0.35)
    second = tool_offset_from_click(PixelPoint(100, 100), PixelPoint(96, 93), m)
    total = (prior[0] + second[0], prior[1] + second[1])
    assert total[0] > prior[0] and total[1] > prior[1]


_self_check()
