from ..common import KlippyState as KlippyState, RequestType as RequestType, TransportType as TransportType, WebRequest as WebRequest
from ..confighelper import ConfigHelper as ConfigHelper
from .file_manager.file_manager import FileManager as FileManager
from .job_queue import JobQueue as JobQueue
from .klippy_apis import KlippyAPI as APIComp
from .klippy_connection import KlippyConnection as KlippyConnection
from _typeshed import Incomplete
from typing import Any

OCTO_VERSION: str

class OctoPrintCompat:
    server: Incomplete
    software_version: Incomplete
    enable_ufp: bool
    webcam: dict[str, Any]
    klippy_apis: APIComp
    heaters: dict[str, dict[str, Any]]
    last_print_stats: dict[str, Any]
    def __init__(self, config: ConfigHelper) -> None: ...
    def printer_state(self) -> str: ...
    def printer_temps(self) -> dict[str, Any]: ...

def load_component(config: ConfigHelper) -> OctoPrintCompat: ...
