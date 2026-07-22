"""Klipper motion helpers for Cam Sight."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Awaitable, Callable

logger = logging.getLogger(__name__)

RunGcode = Callable[[str], Awaitable[None]]


@dataclass(frozen=True)
class MotionPrefs:
    z_approach: float
    z_measure: float
    travel_speed: int


def clamp_z_approach(approach: float, measure: float) -> float:
    return max(approach, measure)


assert clamp_z_approach(10, 37) == 37
assert clamp_z_approach(10, 3) == 10


async def get_position(klippy: Any) -> tuple[float, float, float]:
    result = await klippy.query_objects({"toolhead": ["position"]})
    pos = result.get("toolhead", {}).get("position", [0, 0, 0])
    return float(pos[0]), float(pos[1]), float(pos[2])


async def is_ready(klippy: Any) -> bool:
    info = await klippy.get_klippy_info(default={})
    return info.get("state") == "ready"


async def is_homed(klippy: Any) -> bool:
    status = await klippy.query_objects(
        {"toolhead": ["homed_axes"]}, default={}
    )
    return status.get("toolhead", {}).get("homed_axes", "") == "xyz"


async def require_homed(server: Any, klippy: Any) -> None:
    if not await is_homed(klippy):
        raise server.error("Printer not homed - home XYZ before moving")


async def run_gcode(klippy: Any, script: str) -> None:
    if "SET_GCODE_OFFSET" in script:
        logger.info("cam_sight gcode_offset >> %s", script)
    await klippy.run_gcode(script)


async def move_to_xy(
    klippy: Any,
    server: Any,
    prefs: MotionPrefs,
    x: float,
    y: float,
) -> None:
    await require_homed(server, klippy)
    await run_gcode(klippy, "G90")
    await run_gcode(klippy, f"G1 Z{prefs.z_approach:.4f} F{prefs.travel_speed}")
    await run_gcode(klippy, f"G1 X{x:.4f} Y{y:.4f} F{prefs.travel_speed}")
    await run_gcode(klippy, f"G1 Z{prefs.z_measure:.4f} F500")
    await asyncio.sleep(0.3)


async def return_to_xy(
    klippy: Any,
    server: Any,
    prefs: MotionPrefs,
    x: float,
    y: float,
) -> None:
    await require_homed(server, klippy)
    await run_gcode(klippy, "G90")
    await run_gcode(klippy, f"G1 X{x:.4f} Y{y:.4f} F{prefs.travel_speed}")
    await asyncio.sleep(0.3)


async def jog_axis(
    klippy: Any,
    server: Any,
    prefs: MotionPrefs,
    axis: str,
    delta_mm: float,
) -> None:
    await require_homed(server, klippy)
    x, y, _ = await get_position(klippy)
    await run_gcode(klippy, "G90")
    if axis == "x":
        await run_gcode(klippy, f"G1 X{x + delta_mm:.4f} F{prefs.travel_speed}")
    else:
        await run_gcode(klippy, f"G1 Y{y + delta_mm:.4f} F{prefs.travel_speed}")
    await asyncio.sleep(0.3)


async def jog_z(klippy: Any, server: Any, delta_mm: float) -> None:
    await require_homed(server, klippy)
    _, _, z = await get_position(klippy)
    await run_gcode(klippy, "G90")
    await run_gcode(klippy, f"G1 Z{z + delta_mm:.4f} F500")
    await asyncio.sleep(0.3)
