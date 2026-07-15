import asyncio
from ..common import APITransport as APITransport, BaseRemoteConnection as BaseRemoteConnection, JobEvent as JobEvent, KlippyState as KlippyState, UserInfo as UserInfo
from ..confighelper import ConfigHelper as ConfigHelper
from ..loghelper import LocalQueueHandler as LocalQueueHandler
from .announcements import Announcements as Announcements
from .application import InternalTransport as InternalTransport
from .database import MoonrakerDatabase as MoonrakerDatabase
from .file_manager.file_manager import FileManager as FileManager
from .http_client import HttpClient as HttpClient
from .job_state import JobState as JobState
from .klippy_apis import KlippyAPI as KlippyAPI
from .klippy_connection import KlippyConnection as KlippyConnection
from .machine import Machine as Machine
from .power import PrinterPower as PrinterPower
from .webcam import WebCam as WebCam, WebcamManager as WebcamManager
from .websockets import WebsocketManager as WebsocketManager
from _typeshed import Incomplete
from tornado.websocket import WebSocketClientConnection as WebSocketClientConnection
from typing import Any, Awaitable

COMPONENT_VERSION: str
SP_VERSION: str
TEST_ENDPOINT: Incomplete
PROD_ENDPOINT: Incomplete
CONNECTION_ERROR_LOG_TIME: float
PRE_SETUP_EVENTS: Incomplete

class SimplyPrint(APITransport):
    server: Incomplete
    eventloop: Incomplete
    job_state: JobState
    klippy_apis: KlippyAPI
    spdb: Incomplete
    sp_info: Incomplete
    is_closing: bool
    ws: WebSocketClientConnection | None
    cache: Incomplete
    amb_detect: Incomplete
    layer_detect: Incomplete
    webcam_stream: Incomplete
    print_handler: Incomplete
    last_received_temps: dict[str, float]
    last_err_log_time: float
    last_cpu_update_time: float
    intervals: dict[str, float]
    printer_status: dict[str, dict[str, Any]]
    heaters: dict[str, str]
    missed_job_events: list[dict[str, Any]]
    announce_mutex: Incomplete
    connection_task: asyncio.Task | None
    reconnect_delay: float
    reconnect_token: str | None
    ping_sp_timer: Incomplete
    printer_info_timer: Incomplete
    next_temp_update_time: float
    gcode_terminal_enabled: bool
    connected: bool
    is_set_up: bool
    test: Incomplete
    connect_url: Incomplete
    power_id: str
    filament_sensor: str
    def __init__(self, config: ConfigHelper) -> None: ...
    async def component_init(self) -> None: ...
    def save_item(self, name: str, data: Any): ...
    def send_status(self, status: dict[str, Any], eventtime: float) -> None: ...
    def send_sp(self, evt_name: str, data: Any) -> Awaitable[bool]: ...
    async def close(self) -> None: ...

class ReportCache:
    state: str
    temps: dict[str, Any]
    metadata: dict[str, Any]
    mesh: dict[str, Any]
    job_info: dict[str, Any]
    exclude_object_status: dict[str, Any]
    active_extruder: str
    firmware_info: dict[str, Any]
    machine_info: dict[str, Any]
    cpu_info: dict[str, Any]
    throttled_state: dict[str, Any]
    current_wsid: int | None
    filament_state: str
    def __init__(self) -> None: ...
    def reset_print_state(self) -> None: ...

INITIAL_AMBIENT: int
AMBIENT_CHECK_TIME: Incomplete
TARGET_CHECK_TIME: Incomplete
SAMPLE_CHECK_TIME: float

class AmbientDetect:
    CHECK_INTERVAL: int
    server: Incomplete
    simplyprint: Incomplete
    cache: Incomplete
    eventloop: Incomplete
    def __init__(self, config: ConfigHelper, simplyprint: SimplyPrint, initial_ambient: int) -> None: ...
    @property
    def ambient(self) -> int: ...
    @property
    def sensor_name(self) -> str: ...
    def update_ambient(self, sensor_info: dict[str, Any], eventtime: float = ...) -> None: ...
    def start(self) -> None: ...
    def stop(self) -> None: ...

class LayerDetect:
    def __init__(self) -> None: ...
    @property
    def layer(self) -> int: ...
    def update(self, new_pos: list[float]) -> None: ...
    def start(self, metadata: dict[str, Any]) -> None: ...
    def resume(self) -> None: ...
    def stop(self) -> None: ...
    def reset(self) -> None: ...

FALLBACK_URL: str
SP_SNAPSHOT_URL: str

class WebcamStream:
    server: Incomplete
    eventloop: Incomplete
    simplyprint: Incomplete
    webcam_name: Incomplete
    url: Incomplete
    client: HttpClient
    cam: WebCam | None
    def __init__(self, config: ConfigHelper, simplyprint: SimplyPrint) -> None: ...
    @property
    def connected(self) -> bool: ...
    async def intialize_url(self) -> None: ...
    async def test_connection(self) -> None: ...
    async def get_webcam_config(self) -> dict[str, Any]: ...
    async def extract_image(self) -> str: ...
    async def post_image(self, payload: dict[str, Any]) -> None: ...

class PrintHandler:
    simplyprint: Incomplete
    server: Incomplete
    eventloop: Incomplete
    cache: Incomplete
    download_task: asyncio.Task | None
    print_ready_event: asyncio.Event
    download_progress: int
    pending_file: str
    last_started: str
    sp_user: Incomplete
    def __init__(self, simplyprint: SimplyPrint) -> None: ...
    def download_file(self, url: str, start: bool): ...
    def cancel(self) -> None: ...
    def notify_ready(self) -> None: ...
    async def start_print(self) -> None: ...

class ProtoLogger:
    queue_handler: Incomplete
    qlistner: Incomplete
    def __init__(self, config: ConfigHelper) -> None: ...
    def info(self, msg: str) -> None: ...
    def debug(self, msg: str) -> None: ...
    def warning(self, msg: str) -> None: ...
    def exception(self, msg: str) -> None: ...
    def close(self) -> None: ...

def load_component(config: ConfigHelper) -> SimplyPrint: ...
