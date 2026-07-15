# klipper-cam-sight Moonraker component
#
# Symlinked into moonraker/moonraker/components/cam_sight.py by install.py

from __future__ import annotations
from moonraker.components.application import MoonrakerApp

import asyncio
import json
import logging
import os
import sys
from typing import TYPE_CHECKING, Any

PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if PLUGIN_ROOT not in sys.path:
    sys.path.insert(0, PLUGIN_ROOT)

from component import motion
from lib.cache import TtlCache
from lib.klippy_probe import (
    BACKEND_PROBE_CACHE_ID,
    KlipperProbe,
    MACRO_NAME_RE,
)
from lib.session import SessionState, WizardStep
from lib.status_builder import build_status_dict
from lib.tool_backend import (
    BaseToolBackend,
    BackendId,
    ToolBackend,
    backend_for_id,
    resolve_tool_backend,
)

if TYPE_CHECKING:
    from moonraker.confighelper import ConfigHelper
    from moonraker.server import WebRequest

logger = logging.getLogger(__name__)

DB_NAMESPACE = "cam_sight"
DB_SESSION_KEY = "session"
DB_SAVED_OFFSETS_KEY = "saved_offsets"
DB_PREFS_KEY = "prefs"

class CamSight:
    def __init__(self, confighelper: ConfigHelper) -> None:
        self.server = confighelper.get_server()
        self.klippy = self.server.lookup_component("klippy_apis")
        self.database = self.server.lookup_component("database")

        self.webcam_name = "webcam"
        self.camera_x = 150.0
        self.camera_y = 150.0
        self.z_approach = 10.0
        self.z_measure = 3.0
        self.travel_speed = 3000
        self.known_jog_mm = 1.0
        self.tool_count = 4

        self.macros: list[str] = []
        self._probe = KlipperProbe()
        self.snapshot_url = ""
        self.session = SessionState.fresh()
        self._busy = False
        # last Save snapshot; also in Moonraker DB under saved_offsets
        self._saved_offsets: dict[int, tuple[float, float]] = {}
        self._backend: ToolBackend = BaseToolBackend()
        self._detected_backend_id: str = BackendId.BASE.value
        self._backend_override: str | None = None

        self._register_endpoints()
        self._serve_frontend()

    def _register_endpoints(self) -> None:
        routes = [
            ("/machine/cam_sight/status", ["GET"], self.get_status),
            ("/machine/cam_sight/offset_debug", ["GET"], self.offset_debug),
            ("/machine/cam_sight/calibrate/click", ["POST"], self.calibrate_click),
            ("/machine/cam_sight/undo", ["POST"], self.undo_pick),
            ("/machine/cam_sight/tool0/click", ["POST"], self.tool0_click),
            ("/machine/cam_sight/tool/click", ["POST"], self.tool_click),
            ("/machine/cam_sight/move_to_camera", ["POST"], self.move_to_camera),
            ("/machine/cam_sight/move_to_tool0", ["POST"], self.move_to_tool0),
            ("/machine/cam_sight/jog_z", ["POST"], self.jog_z),
            ("/machine/cam_sight/save_offsets", ["POST"], self.save_offsets),
            ("/machine/cam_sight/clear_offset", ["POST"], self.clear_offset),
            ("/machine/cam_sight/reset", ["POST"], self.reset_offsets),
            ("/machine/cam_sight/reset_all", ["POST"], self.reset_all),
            ("/machine/cam_sight/emergency_stop", ["POST"], self.emergency_stop),
            ("/machine/cam_sight/select_tool", ["POST"], self.select_tool),
            ("/machine/cam_sight/goto_step", ["POST"], self.goto_step),
            ("/machine/cam_sight/select_webcam", ["POST"], self.select_webcam),
            ("/machine/cam_sight/update_prefs", ["POST"], self.update_prefs),
            ("/machine/cam_sight/set_tool_count", ["POST"], self.set_tool_count),
            ("/machine/cam_sight/set_macros", ["POST"], self.set_macros),
            ("/machine/cam_sight/set_backend", ["POST"], self.set_backend),
            ("/machine/cam_sight/run_macro", ["POST"], self.run_macro),
        ]
        for uri, methods, handler in routes:
            self.server.register_endpoint(uri, methods, handler)

    def _serve_frontend(self) -> None:
        dist = os.path.join(PLUGIN_ROOT, "frontend", "dist")
        if not os.path.isdir(dist):
            logger.warning("cam_sight: frontend/dist not found - pull latest from git")
            return

        # register_static_file_handler uses FileRequestHandler, which sets
        # Content-Disposition: attachment - browsers download instead of render.
        try:
            from moonraker.components.application import AuthorizedFileHandler
        except ImportError:
            logger.warning("cam_sight: cannot import AuthorizedFileHandler")
            return

        app: MoonrakerApp = self.server.lookup_component("application")
        prefix = getattr(app, "_route_prefix", "")
        pattern = f"{prefix}/server/files/cam_sight/(.*)"
        app.mutable_router.add_handler(
            pattern,
            AuthorizedFileHandler,
            {"path": dist, "default_filename": "index.html"},
        )
        logger.info("cam_sight: serving UI from %s at /server/files/cam_sight/", dist)

    async def component_init(self) -> None:
        await self._load_session()
        await self._load_saved_offsets()
        await self._load_prefs()
        await self._refresh_snapshot_url()

    async def _load_session(self) -> None:
        stored = self.database.get_item(DB_NAMESPACE, DB_SESSION_KEY, {})
        if isinstance(stored, asyncio.Future):
            stored = await stored
        if stored:
            self.session = SessionState.from_dict(stored)

    async def _load_saved_offsets(self) -> None:
        stored = self.database.get_item(DB_NAMESPACE, DB_SAVED_OFFSETS_KEY, {})
        if isinstance(stored, asyncio.Future):
            stored = await stored
        if stored:
            self._saved_offsets = {
                int(k): (float(v[0]), float(v[1])) for k, v in stored.items()
            }

    async def _persist_saved_offsets(self) -> None:
        payload = {str(k): [v[0], v[1]] for k, v in sorted(self._saved_offsets.items())}
        fut = self.database.insert_item(DB_NAMESPACE, DB_SAVED_OFFSETS_KEY, payload)
        if isinstance(fut, asyncio.Future):
            await fut

    def _prefs_dict(self) -> dict[str, Any]:
        return {
            "webcam_name": self.webcam_name,
            "camera_x": self.camera_x,
            "camera_y": self.camera_y,
            "z_approach": self.z_approach,
            "z_measure": self.z_measure,
            "travel_speed": self.travel_speed,
            "known_jog_mm": self.known_jog_mm,
            "tool_count": self.tool_count,
            "macros": list(self.macros),
            "backend_override": self._backend_override,
        }

    async def _load_prefs(self) -> None:
        stored = self.database.get_item(DB_NAMESPACE, DB_PREFS_KEY, {})
        if isinstance(stored, asyncio.Future):
            stored = await stored
        if not stored:
            return
        if "webcam_name" in stored:
            self.webcam_name = str(stored["webcam_name"])
        if "camera_x" in stored:
            self.camera_x = float(stored["camera_x"])
        if "camera_y" in stored:
            self.camera_y = float(stored["camera_y"])
        if "z_approach" in stored:
            self.z_approach = float(stored["z_approach"])
        if "z_measure" in stored:
            self.z_measure = float(stored["z_measure"])
        if "travel_speed" in stored:
            self.travel_speed = int(stored["travel_speed"])
        if "known_jog_mm" in stored:
            self.known_jog_mm = float(stored["known_jog_mm"])
        if "tool_count" in stored:
            self.tool_count = max(1, int(stored["tool_count"]))
        if "macros" in stored and isinstance(stored["macros"], list):
            self.macros = [
                str(m) for m in stored["macros"] if MACRO_NAME_RE.match(str(m))
            ]
        if "backend_override" in stored:
            raw = stored["backend_override"]
            if raw in (None, "", "auto"):
                self._backend_override = None
            elif raw in (BackendId.BASE.value, BackendId.INDX.value):
                self._backend_override = str(raw)
            else:
                logger.warning("cam_sight: ignoring invalid backend_override: %s", raw)

    async def _persist_prefs(self) -> None:
        fut = self.database.insert_item(DB_NAMESPACE, DB_PREFS_KEY, self._prefs_dict())
        if isinstance(fut, asyncio.Future):
            await fut

    def _list_webcams(self) -> list[str]:
        try:
            webcam = self.server.lookup_component("webcam")
            return sorted(webcam.get_webcams().keys())
        except Exception:
            return []

    @staticmethod
    def _validate_macro_name(name: str) -> str:
        if not MACRO_NAME_RE.match(name):
            raise ValueError(f"Invalid macro name: {name}")
        return name

    def _offsets_dirty(self) -> bool:
        current = {
            k: (round(v[0], 6), round(v[1], 6))
            for k, v in self.session.saveable_offsets().items()
        }
        saved = {
            k: (round(v[0], 6), round(v[1], 6)) for k, v in self._saved_offsets.items()
        }
        return current != saved

    async def _save_session(self) -> None:
        fut = self.database.insert_item(
            DB_NAMESPACE, DB_SESSION_KEY, self.session.to_dict()
        )
        if isinstance(fut, asyncio.Future):
            await fut

    async def _refresh_snapshot_url(self) -> None:
        try:
            webcam = self.server.lookup_component("webcam")
            cams = webcam.get_webcams()  # name -> WebCam
            wc = cams.get(self.webcam_name)
            if wc is None and cams:
                wc = next(iter(cams.values()))
            if wc is not None:
                self.snapshot_url = wc.snapshot_url or ""
        except Exception as exc:
            logger.warning("cam_sight: could not resolve webcam: %s", exc)

    def _body(self, webrequest: WebRequest) -> dict[str, Any]:
        args = webrequest.get_args()
        if args:
            return dict(args)
        raw = webrequest.get_request_body()
        if raw:
            return json.loads(raw)
        return {}

    def _motion_prefs(self) -> motion.MotionPrefs:
        return motion.MotionPrefs(
            self.z_approach, self.z_measure, self.travel_speed
        )

    def _status_dict(self) -> dict[str, Any]:
        return build_status_dict(
            session=self.session,
            snapshot_url=self.snapshot_url,
            webcam_name=self.webcam_name,
            webcams=self._list_webcams(),
            camera_x=self.camera_x,
            camera_y=self.camera_y,
            z_approach=self.z_approach,
            z_measure=self.z_measure,
            travel_speed=self.travel_speed,
            known_jog_mm=self.known_jog_mm,
            macros=self.macros,
            available_macros=list(self._probe.macro_cache.stale or []),
            busy=self._busy,
            tool_count=self.tool_count,
            offsets_dirty=self._offsets_dirty(),
            detected_backend_id=self._detected_backend_id,
            backend_override=self._backend_override,
            backend=self._backend,
        )

    async def _apply_synced_tool_count(self, backend_id: str) -> None:
        count = await self._probe.synced_tool_count(self.klippy, backend_id)
        if count is not None and count != self.tool_count:
            self.tool_count = count
            if self.session.selected_tool >= count:
                self.session.selected_tool = count - 1
                await self._save_session()

    async def _resolve_backend(self) -> None:
        has_indx = await self._probe.has_indx_section(self.klippy, self._is_ready)
        if has_indx is None:
            if self._backend_override is None:
                return
            self._backend = backend_for_id(self._backend_override)
            await self._apply_synced_tool_count(self._backend.id.value)
            return
        detected = resolve_tool_backend(has_indx_section=has_indx)
        self._detected_backend_id = detected.id.value
        if self._backend_override is not None:
            self._backend = backend_for_id(self._backend_override)
        else:
            self._backend = detected
        await self._apply_synced_tool_count(self._backend.id.value)

    async def get_status(self, webrequest: WebRequest) -> dict[str, Any]:
        await self._probe.list_macros(self.klippy, self._is_ready)
        await self._resolve_backend()
        return self._status_dict()

    async def offset_debug(self, webrequest: WebRequest) -> dict[str, Any]:
        """Snapshot session offsets + live Klipper gcode_move state."""
        return {
            "selected_tool": self.session.selected_tool,
            "session_offsets": self._session_offsets_dict(),
            "klippy": await self._fetch_offset_state(),
        }

    async def _run_gcode(self, script: str) -> None:
        await motion.run_gcode(self.klippy, script)

    async def _fetch_offset_state(self) -> dict[str, Any]:
        try:
            return await self.klippy.query_objects(
                {
                    "gcode_move": [
                        "gcode_position",
                        "position",
                        "homing_origin",
                        "gcode_offset",
                    ],
                    "toolhead": ["position", "homing_origin"],
                },
                default={},
            )
        except Exception as exc:
            return {"error": str(exc)}

    def _session_offsets_dict(self) -> dict[str, dict[str, float]]:
        return {
            str(k): {"x": v[0], "y": v[1]}
            for k, v in sorted(self.session.offsets.items())
        }

    async def _offset_checkpoint(self, label: str, **ctx: Any) -> None:
        """Log toolhead position + session offsets (grep moonraker.log)."""
        state = await self._fetch_offset_state()
        th = state.get("toolhead", {})
        extra = " ".join(f"{k}={v}" for k, v in ctx.items()) if ctx else ""
        logger.info(
            "cam_sight [%s] tool=T%d session=%s toolhead.position=%s%s",
            label,
            self.session.selected_tool,
            self._session_offsets_dict(),
            th.get("position"),
            f" | {extra}" if extra else "",
        )

    async def _clear_gcode_offset_hygiene(self) -> None:
        """Clear any print-time offset transform without moving (MOVE=0 only)."""
        await self._run_gcode("SET_GCODE_OFFSET X=0 Y=0 Z=0 MOVE=0")

    async def select_tool(self, webrequest: WebRequest) -> dict[str, Any]:
        body = self._body(webrequest)
        tool_index = int(body.get("tool_index", 0))
        prev_tool = self.session.selected_tool
        self.session.selected_tool = tool_index
        await self._save_session()

        if await self._is_ready():
            await self._resolve_backend()
            await self._offset_checkpoint(
                "select_tool:start",
                prev_tool=f"T{prev_tool}",
                new_tool=f"T{tool_index}",
            )

            async def _after_select() -> None:
                await self._backend.select_tool(tool_index, self._run_gcode)
                await self._clear_gcode_offset_hygiene()
                if (
                    self.session.tool0_ref is not None
                    and self.session.wizard_step == WizardStep.TOOL_OFFSET
                ):
                    stored = (
                        self.session.offsets.get(tool_index)
                        if tool_index != 0
                        else None
                    )
                    if stored is not None:
                        ox, oy = stored
                        await self._offset_checkpoint(
                            "select_tool:before_move_t0_plus_offset",
                            tool=f"T{tool_index}",
                            target=f"({ox:.4f},{oy:.4f})",
                        )
                        await self._move_to_tool0_plus_offset(ox, oy)
                        await self._offset_checkpoint(
                            "select_tool:after_move_t0_plus_offset"
                        )
                    else:
                        await self._offset_checkpoint("select_tool:before_move_t0")
                        await self._move_to_tool0_xy()
                        await self._offset_checkpoint("select_tool:after_move_t0")

            await self._guard(_after_select())

        return self._status_dict()

    async def goto_step(self, webrequest: WebRequest) -> dict[str, Any]:
        body = self._body(webrequest)
        step = body.get("step", "")
        try:
            self.session.wizard_step = WizardStep(step)
        except ValueError as exc:
            raise self.server.error(f"Invalid step: {step}") from exc
        await self._save_session()
        return self._status_dict()

    async def select_webcam(self, webrequest: WebRequest) -> dict[str, Any]:
        body = self._body(webrequest)
        name = str(body.get("webcam_name", "")).strip()
        if not name:
            raise self.server.error("webcam_name required")
        cams = self._list_webcams()
        if cams and name not in cams:
            raise self.server.error(f"Unknown webcam: {name}")
        self.webcam_name = name
        await self._refresh_snapshot_url()
        await self._persist_prefs()
        return self._status_dict()

    async def update_prefs(self, webrequest: WebRequest) -> dict[str, Any]:
        body = self._body(webrequest)
        for key in ("camera_x", "camera_y", "z_approach", "z_measure"):
            if key in body:
                setattr(self, key, float(body[key]))
        if "travel_speed" in body:
            speed = int(body["travel_speed"])
            if speed <= 0:
                raise self.server.error("travel_speed must be positive")
            self.travel_speed = speed
        if "known_jog_mm" in body:
            jog = float(body["known_jog_mm"])
            if jog <= 0:
                raise self.server.error("known_jog_mm must be positive")
            self.known_jog_mm = jog
        await self._persist_prefs()
        return self._status_dict()

    async def set_tool_count(self, webrequest: WebRequest) -> dict[str, Any]:
        body = self._body(webrequest)
        count = int(body.get("count", 0))
        if count < 1 or count > 16:
            raise self.server.error("tool count must be 1–16")
        if count < self.tool_count:
            for tool in range(count, self.tool_count):
                if tool == 0:
                    continue
                self.session.offsets.pop(tool, None)
                self.session.offset_history.pop(tool, None)
        self.tool_count = count
        if self.session.selected_tool >= count:
            self.session.selected_tool = count - 1
        await self._persist_prefs()
        await self._save_session()
        return self._status_dict()

    async def set_macros(self, webrequest: WebRequest) -> dict[str, Any]:
        body = self._body(webrequest)
        raw = body.get("macros")
        if not isinstance(raw, list):
            raise self.server.error("macros must be a list")
        try:
            self.macros = [self._validate_macro_name(str(m)) for m in raw]
        except ValueError as exc:
            raise self.server.error(str(exc)) from exc
        await self._persist_prefs()
        return self._status_dict()

    async def set_backend(self, webrequest: WebRequest) -> dict[str, Any]:
        body = self._body(webrequest)
        raw = str(body.get("backend", "")).strip().lower()
        if raw not in (BackendId.BASE.value, BackendId.INDX.value):
            raise self.server.error("backend must be 'base' or 'indx'")
        TtlCache.invalidate(BACKEND_PROBE_CACHE_ID)
        has_indx = await self._probe.has_indx_section(self.klippy, self._is_ready)
        if has_indx is not None:
            self._detected_backend_id = resolve_tool_backend(
                has_indx_section=has_indx
            ).id.value
        if raw == self._detected_backend_id:
            self._backend_override = None
            self._backend = backend_for_id(raw)
        else:
            self._backend_override = raw
            self._backend = backend_for_id(raw)
        await self._apply_synced_tool_count(self._backend.id.value)
        await self._persist_prefs()
        return self._status_dict()

    async def run_macro(self, webrequest: WebRequest) -> dict[str, Any]:
        body = self._body(webrequest)
        name = str(body.get("name", "")).strip()
        try:
            self._validate_macro_name(name)
        except ValueError as exc:
            raise self.server.error(str(exc)) from exc
        if name not in self.macros:
            raise self.server.error(f"Macro not configured: {name}")

        async def _run() -> None:
            await self._run_gcode(name)

        await self._guard(_run())
        return self._status_dict()

    async def _get_position(self) -> tuple[float, float, float]:
        return await motion.get_position(self.klippy)

    async def _is_ready(self) -> bool:
        return await motion.is_ready(self.klippy)

    async def _guard(self, coro) -> Any:
        if self._busy:
            raise self.server.error("Busy - wait for the current move")
        if not await self._is_ready():
            raise self.server.error("Klipper is not ready")
        self._busy = True
        try:
            return await coro
        finally:
            self._busy = False

    async def move_to_camera(self, webrequest: WebRequest) -> dict[str, Any]:
        async def _move() -> None:
            await self._clear_gcode_offset_hygiene()
            await motion.move_to_xy(
                self.klippy,
                self.server,
                self._motion_prefs(),
                self.camera_x,
                self.camera_y,
            )

        await self._guard(_move())
        return self._status_dict()

    async def _move_to_xy(self, x: float, y: float) -> None:
        await motion.move_to_xy(
            self.klippy, self.server, self._motion_prefs(), x, y
        )

    async def _move_to_tool0_xy(self) -> None:
        if self.session.tool0_ref is None:
            raise self.server.error("Tool 0 reference not set")
        ref = self.session.tool0_ref
        await self._move_to_xy(ref.machine_x, ref.machine_y)

    async def _move_to_tool0_plus_offset(self, ox: float, oy: float) -> None:
        if self.session.tool0_ref is None:
            raise self.server.error("Tool 0 reference not set")
        ref = self.session.tool0_ref
        await self._move_to_xy(ref.machine_x + ox, ref.machine_y + oy)

    async def move_to_tool0(self, webrequest: WebRequest) -> dict[str, Any]:
        async def _move() -> None:
            await self._clear_gcode_offset_hygiene()
            await self._move_to_tool0_xy()

        await self._guard(_move())
        return self._status_dict()

    async def _return_to_xy(self, x: float, y: float) -> None:
        await motion.return_to_xy(
            self.klippy, self.server, self._motion_prefs(), x, y
        )

    async def _jog_axis(self, axis: str, delta_mm: float) -> None:
        await motion.jog_axis(
            self.klippy, self.server, self._motion_prefs(), axis, delta_mm
        )

    async def _jog_z(self, delta_mm: float) -> None:
        await motion.jog_z(self.klippy, self.server, delta_mm)

    async def jog_z(self, webrequest: WebRequest) -> dict[str, Any]:
        delta_mm = float(self._body(webrequest)["delta_mm"])

        async def _move() -> None:
            await self._jog_z(delta_mm)

        await self._guard(_move())
        return self._status_dict()

    async def calibrate_click(self, webrequest: WebRequest) -> dict[str, Any]:
        body = self._body(webrequest)
        px = float(body["px"])
        py = float(body["py"])
        cal = self.session.calibration

        if cal.origin is None:
            mx, my, _ = await self._get_position()
            self.session.set_calibration_origin(px, py, mx, my)
            await self._save_session()

            async def _after_origin() -> None:
                await self._jog_axis("x", self.known_jog_mm)

            await self._guard(_after_origin())
            return self._status_dict()

        if cal.after_x is None:
            self.session.set_calibration_after_x(px, py)
            await self._save_session()
            origin = cal.origin_machine_xy
            if origin is None:
                raise self.server.error("Calibration origin lost - reset and retry")
            x, y = origin

            async def _after_x() -> None:
                await self._return_to_xy(x, y)
                await self._jog_axis("y", self.known_jog_mm)

            await self._guard(_after_x())
            return self._status_dict()

        if cal.after_y is None:
            self.session.set_calibration_after_y(px, py)
            origin = cal.origin_machine_xy
            try:
                self.session.finish_calibration(self.known_jog_mm)
            except ValueError as exc:
                self.session.calibration.reset()
                await self._save_session()
                raise self.server.error(str(exc)) from exc

            if origin is not None:

                async def _finish() -> None:
                    await self._return_to_xy(origin[0], origin[1])

                await self._guard(_finish())

            self.session.wizard_step = WizardStep.TOOL0_REF
            await self._save_session()
            return self._status_dict()

        raise self.server.error(
            "Calibration already complete - reset or continue wizard"
        )

    async def undo_pick(self, webrequest: WebRequest) -> dict[str, Any]:
        undone = self.session.undo_last()
        if undone is None:
            raise self.server.error("Nothing to undo")
        kind, origin_xy = undone
        await self._save_session()

        if kind == "origin" and origin_xy is not None:

            async def _move() -> None:
                await self._return_to_xy(origin_xy[0], origin_xy[1])

            await self._guard(_move())
        elif kind == "after_x" and origin_xy is not None:

            async def _move() -> None:
                await self._return_to_xy(origin_xy[0], origin_xy[1])
                await self._jog_axis("x", self.known_jog_mm)

            await self._guard(_move())

        return self._status_dict()

    async def tool0_click(self, webrequest: WebRequest) -> dict[str, Any]:
        body = self._body(webrequest)
        px = float(body["px"])
        py = float(body["py"])
        mx, my, _ = await self._get_position()
        self.session.record_tool0(px, py, mx, my)
        self.session.wizard_step = WizardStep.TOOL_OFFSET
        await self._save_session()
        return self._status_dict()

    async def tool_click(self, webrequest: WebRequest) -> dict[str, Any]:
        body = self._body(webrequest)
        px = float(body["px"])
        py = float(body["py"])
        tool_index = int(body.get("tool_index", self.session.selected_tool))
        try:
            total, residual = self.session.apply_tool_click(tool_index, px, py)
        except RuntimeError as exc:
            raise self.server.error(str(exc)) from exc
        self.session.selected_tool = tool_index
        await self._save_session()
        await self._offset_checkpoint(
            "tool_click:stored",
            tool=f"T{tool_index}",
            total=f"({total[0]:.4f},{total[1]:.4f})",
            residual=f"({residual[0]:.4f},{residual[1]:.4f})",
            note="auto_move_to_t0_plus_total",
        )

        if tool_index != 0:
            tx, ty = total

            async def _move_corrected() -> None:
                await self._clear_gcode_offset_hygiene()
                await self._offset_checkpoint(
                    "tool_click:before_move_corrected",
                    tool=f"T{tool_index}",
                    target=f"({tx:.4f},{ty:.4f})",
                )
                await self._move_to_tool0_plus_offset(tx, ty)
                await self._offset_checkpoint("tool_click:after_move_corrected")

            await self._guard(_move_corrected())

        return self._status_dict()

    async def save_offsets(self, webrequest: WebRequest) -> dict[str, Any]:
        to_save = self.session.saveable_offsets()
        if not to_save:
            raise self.server.error("Tool 0 reference not set - nothing to save")

        async def _save() -> None:
            await self._clear_gcode_offset_hygiene()
            for tool, (ox, oy) in sorted(to_save.items()):
                names = self._backend.save_variable_names(tool)
                await self._run_gcode(
                    f"SAVE_VARIABLE VARIABLE={names.x} VALUE={ox:.6f}"
                )
                await self._run_gcode(
                    f"SAVE_VARIABLE VARIABLE={names.y} VALUE={oy:.6f}"
                )

        if await self._is_ready():
            await self._resolve_backend()
            await self._guard(_save())
        else:
            raise self.server.error("Klipper is not ready")
        self._saved_offsets = dict(to_save)
        await self._persist_saved_offsets()
        logger.info("cam_sight: saved offsets to save_variables: %s", to_save)
        return self._status_dict()

    async def clear_offset(self, webrequest: WebRequest) -> dict[str, Any]:
        body = self._body(webrequest)
        tool_index = int(body.get("tool_index", -1))
        if tool_index == 0:
            raise self.server.error("Cannot clear tool 0 offset")
        try:
            self.session.clear_tool_offset(tool_index)
        except ValueError as exc:
            raise self.server.error(str(exc)) from exc
        await self._save_session()
        await self._offset_checkpoint(
            "clear_offset:session_cleared",
            tool=f"T{tool_index}",
        )

        async def _after_clear() -> None:
            await self._clear_gcode_offset_hygiene()
            if self.session.tool0_ref is not None:
                await self._offset_checkpoint("clear_offset:before_move_t0")
                await self._move_to_tool0_xy()
                await self._offset_checkpoint("clear_offset:after_move_t0")

        if await self._is_ready():
            await self._guard(_after_clear())

        return self._status_dict()

    async def reset_offsets(self, webrequest: WebRequest) -> dict[str, Any]:
        self.session.reset_tool_offsets()
        await self._save_session()
        await self._offset_checkpoint("reset_offsets:session_cleared")

        async def _after_reset() -> None:
            await self._clear_gcode_offset_hygiene()
            if self.session.tool0_ref is not None:
                await self._offset_checkpoint("reset_offsets:before_move_t0")
                await self._move_to_tool0_xy()
                await self._offset_checkpoint("reset_offsets:after_move_t0")

        if await self._is_ready():
            await self._guard(_after_reset())

        return self._status_dict()

    async def reset_all(self, webrequest: WebRequest) -> dict[str, Any]:
        # fresh(0) - drop mm/px calibration; do not re-seed from config default
        self.session = SessionState.fresh(0.0)
        self._saved_offsets = {}
        await self._save_session()
        await self._persist_saved_offsets()
        await self._offset_checkpoint("reset_all:session_cleared")

        if await self._is_ready():
            await self._guard(self._clear_gcode_offset_hygiene())

        return self._status_dict()

    async def emergency_stop(self, webrequest: WebRequest) -> dict[str, Any]:
        try:
            await self.klippy.emergency_stop()
        except Exception:
            pass
        return {"ok": True}


def load_component(config: ConfigHelper) -> CamSight:
    return CamSight(config)
