from ..confighelper import ConfigHelper as ConfigHelper
from ..utils import ServerError as ServerError, async_serial as async_serial
from .file_manager.file_manager import FileManager as FMComp
from .klippy_apis import KlippyAPI as APIComp
from .klippy_connection import KlippyConnection as KlippyConnection
from _typeshed import Incomplete
from typing import Any, Callable, Coroutine, Deque

FlexCallback = Callable[..., Coroutine | None]
MIN_EST_TIME: float
INITIALIZE_TIMEOUT: float

class PanelDueError(ServerError): ...

RESTART_GCODES: Incomplete

class PanelDue:
    server: Incomplete
    event_loop: Incomplete
    file_manager: FMComp
    klippy_apis: APIComp
    kinematics: str
    machine_name: Incomplete
    firmware_name: str
    last_message: str | None
    last_gcode_response: str | None
    current_file: str
    file_metadata: dict[str, Any]
    enable_checksum: Incomplete
    debug_queue: Deque[str]
    enabled: bool
    printer_state: dict[str, dict[str, Any]]
    extruder_count: int
    heaters: list[str]
    is_ready: bool
    is_shutdown: bool
    initialized: bool
    cq_busy: bool
    gq_busy: bool
    command_queue: list[tuple[FlexCallback, Any, Any]]
    gc_queue: list[str]
    last_printer_state: str
    last_update_time: float
    confirmed_gcode: str
    mbox_sequence: int
    available_macros: dict[str, str]
    confirmed_macros: Incomplete
    non_trivial_keys: Incomplete
    ser_conn: Incomplete
    direct_gcodes: dict[str, FlexCallback]
    special_gcodes: dict[str, Callable[[list[str]], str]]
    def __init__(self, config: ConfigHelper) -> None: ...
    async def run_serial(self) -> None: ...
    serial_task: Incomplete
    async def component_init(self) -> None: ...
    def paneldue_beep(self, frequency: int, duration: float) -> None: ...
    def process_line(self, line: str) -> None: ...
    def queue_gcode(self, script: str) -> None: ...
    def queue_command(self, cmd: FlexCallback, *args, **kwargs) -> None: ...
    def handle_gcode_response(self, response: str) -> None: ...
    def write_response(self, response: dict[str, Any]) -> None: ...
    async def close(self) -> None: ...

def load_component(config: ConfigHelper) -> PanelDue: ...
