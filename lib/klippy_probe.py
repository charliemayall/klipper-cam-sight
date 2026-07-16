"""Cached Klipper probes: macro list, INDX detection, tool count sync."""

from __future__ import annotations

import logging
import re
from typing import Any, Awaitable, Callable

from lib.cache import TtlCache, ttl_cache
from lib.tool_backend import backend_for_id

logger = logging.getLogger(__name__)

MACRO_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
GCODE_MACRO_PREFIX = "gcode_macro "
MACRO_CACHE_TTL = 30.0
BACKEND_PROBE_TTL = 30.0
BACKEND_PROBE_CACHE_ID = "backend_probe"
MACRO_CACHE_ID = "macros"
OBJECT_LIST_CACHE_ID = "object_list"
TOOL_POSITIONS_MACRO = "gcode_macro TOOL_POSITIONS"

IsReady = Callable[[], Awaitable[bool]]


def indx_detected_in_objects(objects: list[str]) -> bool:
    return "indx" in objects or TOOL_POSITIONS_MACRO in objects


def macro_names_from_klippy_objects(objects: list[str]) -> list[str]:
    names = [
        obj[len(GCODE_MACRO_PREFIX) :]
        for obj in objects
        if obj.startswith(GCODE_MACRO_PREFIX)
        and MACRO_NAME_RE.match(obj[len(GCODE_MACRO_PREFIX) :])
    ]
    return sorted(names)


class KlipperProbe:
    def __init__(self) -> None:
        self._object_list_cache: TtlCache[list[str]] = TtlCache(
            MACRO_CACHE_TTL, cache_id=OBJECT_LIST_CACHE_ID
        )
        self._macro_cache: TtlCache[list[str]] = TtlCache(
            MACRO_CACHE_TTL, cache_id=MACRO_CACHE_ID
        )

    @property
    def macro_cache(self) -> TtlCache[list[str]]:
        return self._macro_cache

    async def _get_object_list(self, klippy: Any, is_ready: IsReady) -> list[str]:
        async def fetch() -> list[str] | None:
            if not await is_ready():
                return None
            try:
                objects = await klippy.get_object_list(default=[])
            except Exception as exc:
                logger.warning("cam_sight: could not list klipper objects: %s", exc)
                return None
            if isinstance(objects, list):
                return objects
            return None

        return await self._object_list_cache.get_or_fetch(
            fetch,
            fallback=lambda: list(self._object_list_cache.stale or []),
        )

    async def list_macros(self, klippy: Any, is_ready: IsReady) -> list[str]:
        objects = await self._get_object_list(klippy, is_ready)
        macros = macro_names_from_klippy_objects(objects)
        self._macro_cache.set(macros)
        return list(macros)

    @ttl_cache(
        ttl_seconds=BACKEND_PROBE_TTL,
        cache_id=BACKEND_PROBE_CACHE_ID,
        is_cacheable=lambda x: x is not None,
    )
    async def has_indx_section(self, klippy: Any, is_ready: IsReady) -> bool | None:
        if not await is_ready():
            return None
        objects = await self._get_object_list(klippy, is_ready)
        if not objects:
            return None
        return indx_detected_in_objects(objects)

    @ttl_cache(
        ttl_seconds=BACKEND_PROBE_TTL,
        cache_id=BACKEND_PROBE_CACHE_ID,
        is_cacheable=lambda _: True,
    )
    async def synced_tool_count(self, klippy: Any, backend_id: str) -> int | None:
        backend = backend_for_id(backend_id)
        if not backend.flags.syncs_tool_count:
            return None
        return await backend.sync_tool_count(klippy.query_objects)


def _self_check() -> None:
    assert macro_names_from_klippy_objects(
        ["toolhead", "gcode_macro FOO", "gcode_macro _BAR", "gcode_macro 9BAD"]
    ) == ["FOO", "_BAR"]
    assert indx_detected_in_objects(["toolhead", "indx"]) is True
    assert indx_detected_in_objects(["gcode_macro TOOL_POSITIONS"]) is True
    assert indx_detected_in_objects(["toolhead", "extruder"]) is False


_self_check()
