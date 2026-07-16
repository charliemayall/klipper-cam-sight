"""Toolchanger backends - SAVE_VARIABLE naming + tool-related macro exec."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Awaitable, Callable

RunGcode = Callable[[str], Awaitable[None]]
QueryObjects = Callable[..., Awaitable[Any]]


class BackendId(str, Enum):
    BASE = "base"
    INDX = "indx"


@dataclass(frozen=True)
class BackendFlags:
    """Capability flags the UI can branch on without knowing INDX."""

    auto_toolchange: bool
    requires_apply_macro: bool
    syncs_tool_count: bool


@dataclass(frozen=True)
class SaveVariableNames:
    x: str
    y: str


class ToolBackend(ABC):
    """All tool-related Klipper macro exec goes through here."""

    id: BackendId
    flags: BackendFlags

    @abstractmethod
    def save_variable_names(self, tool: int) -> SaveVariableNames:
        """SAVE_VARIABLE names for this tool's XY offsets."""

    async def select_tool(self, tool: int, run_gcode: RunGcode) -> None:
        """Physical tool swap before cal hygiene + jog. Default: no-op."""
        return None

    async def sync_tool_count(self, query_objects: QueryObjects) -> int | None:
        """Configured tool count, or None if backend doesn't own it."""
        return None

    def status_dict(self) -> dict[str, Any]:
        return {
            "backend": self.id.value,
            "backend_flags": asdict(self.flags),
        }


class BaseToolBackend(ToolBackend):
    id = BackendId.BASE
    flags = BackendFlags(
        auto_toolchange=False,
        requires_apply_macro=True,
        syncs_tool_count=False,
    )

    def save_variable_names(self, tool: int) -> SaveVariableNames:
        return SaveVariableNames(
            x=f"cam_sight_t{tool}_x",
            y=f"cam_sight_t{tool}_y",
        )


class IndxToolBackend(ToolBackend):
    id = BackendId.INDX
    flags = BackendFlags(
        auto_toolchange=True,
        requires_apply_macro=False,
        syncs_tool_count=True,
    )

    def save_variable_names(self, tool: int) -> SaveVariableNames:
        return SaveVariableNames(
            x=f"t{tool}_offset_x",
            y=f"t{tool}_offset_y",
        )

    async def select_tool(self, tool: int, run_gcode: RunGcode) -> None:
        # Match INDX CAL_02 - SKIP_Z_CORRECTION fixed upstream (Bondtech PR)
        await run_gcode(f"CHANGE_TOOL TOOL={tool} SKIP_Z_CORRECTION=1")

    async def sync_tool_count(self, query_objects: QueryObjects) -> int | None:
        try:
            status = await query_objects(
                {"gcode_macro TOOL_POSITIONS": ["tool_count"]},
                default={},
            )
        except Exception:
            return None
        tp = status.get("gcode_macro TOOL_POSITIONS") or {}
        raw = tp.get("tool_count")
        if raw is None:
            return None
        count = int(raw)
        if count < 1 or count > 16:
            return None
        return count


def resolve_tool_backend(*, has_indx_section: bool) -> ToolBackend:
    if has_indx_section:
        return IndxToolBackend()
    return BaseToolBackend()


def backend_for_id(backend_id: str) -> ToolBackend:
    if backend_id == BackendId.INDX.value:
        return IndxToolBackend()
    if backend_id == BackendId.BASE.value:
        return BaseToolBackend()
    raise ValueError(f"Unknown backend: {backend_id}")


# fail loud if naming / resolve drift
assert BaseToolBackend().save_variable_names(1) == SaveVariableNames(
    "cam_sight_t1_x", "cam_sight_t1_y"
)
assert IndxToolBackend().save_variable_names(1) == SaveVariableNames(
    "t1_offset_x", "t1_offset_y"
)
assert resolve_tool_backend(has_indx_section=True).id is BackendId.INDX
assert resolve_tool_backend(has_indx_section=False).id is BackendId.BASE
assert backend_for_id("indx").id is BackendId.INDX
assert backend_for_id("base").id is BackendId.BASE
